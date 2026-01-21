from openai import OpenAI
from dotenv import load_dotenv
from utils import encode_image, INVOICE_DETECTION_SCHEMA, INVOICE_PROPERTIES_SCHEMA

load_dotenv()


class LocalLlama:
    def __init__(self, base_url="http://localhost:8080/v1", api_key="not-needed"):
        self.client = OpenAI(base_url=base_url, api_key=api_key)

    def generate(self, prompt, image_path, response_format, model=None):
        image = encode_image(image_path)
        completion = self.client.chat.completions.create(
            model="",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image}"
                        }
                    }
                ]
            }],
            response_format=response_format,
            temperature=0
        )
        return completion.choices[0].message.content

    def invoice_or_not(self, image_path, model=None):
        prompt = "Is this image a photo of an invoice?"
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "response",
                "strict": True,
                "schema": INVOICE_DETECTION_SCHEMA
            },
            "required": ["invoice"],
            "additionalProperties": False
        }
        return self.generate(prompt, image_path, response_format, model)

    def invoice_properties(self, image_path, model=None):
        prompt = """You are an OCR and information-extraction assistant for invoices.

From the provided invoice image, extract the following fields and output ONLY JSON
matching the given schema:

- invoice_date: the date of the invoice.
- Use ONLY the date printed on the document.
- The document may use German date formats like "30. Juni 1975" or "30.06.1975".
- Convert it to ISO format YYYY-MM-DD (e.g. "1975-06-30").
- If the year or day is missing or unreadable, set this field to null.

- total_amount: the final total amount of the invoice.
- Use the grand total, not intermediate subtotals.
- Remove currency symbols and text (e.g. "DM", "EUR", "$").
- Remove thousand separators and trailing dots, e.g. "31,496.--" → 31496.
- Use "." as decimal separator (e.g. "1234.50").

- currency: the currency of the invoice.
- Map symbols or abbreviations to ISO codes where possible,
    e.g. "€" or "EUR" → "EUR", "DM" → "DEM".
- If unclear, copy the printed currency text exactly.

Use ONLY information visible on the invoice image. Do NOT guess or invent values.
If a field truly cannot be found, set it to null.
Return only valid JSON, no markdown, no comments."""

        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "invoice_schema",
                "strict": True,
                "schema": INVOICE_PROPERTIES_SCHEMA
            }
        }
        return self.generate(prompt, image_path, response_format, model)


def main():
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(description="Test LocalLlama invoice processing")
    parser.add_argument("image_path", nargs="?", default="test_invoice.png",
                        help="Path to the invoice image file")
    parser.add_argument("--url", type=str, default="http://localhost:8080/v1",
                        help="URL of the llama.cpp server")
    args = parser.parse_args()

    try:
        print(f"Connecting to server: {args.url}")
        inferencer = LocalLlama(base_url=args.url)

        print(f"\n--- Testing invoice detection on: {args.image_path} ---")
        result = inferencer.invoice_or_not(args.image_path)
        print(f"Result: {result}")

        invoice_data = json.loads(result)
        if invoice_data.get("invoice"):
            print("\n--- Invoice detected! Extracting properties ---")
            properties = inferencer.invoice_properties(args.image_path)
            print(f"Properties: {properties}")

            props_data = json.loads(properties)
            print("\n--- Extracted Data ---")
            print(f"Date: {props_data.get('invoice_date')}")
            print(f"Total: {props_data.get('total_amount')}")
            print(f"Currency: {props_data.get('currency')}")
        else:
            print("Image is not an invoice.")

    except FileNotFoundError:
        print(f"Error: Could not find file '{args.image_path}'", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON response: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
