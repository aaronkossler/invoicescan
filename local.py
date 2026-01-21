from openai import OpenAI
from dotenv import load_dotenv
from base import BaseInferencer

load_dotenv()


class LocalLlama(BaseInferencer):
    def __init__(self, base_url="http://localhost:8080/v1", api_key="not-needed"):
        self.client = OpenAI(base_url=base_url, api_key=api_key)


def main():
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(description="Test LocalLlama invoice processing")
    parser.add_argument("image_path", nargs="?", default="test_invoice.png",
                        help="Path to the invoice image file")
    parser.add_argument("--url", type=str, default="http://localhost:8080/v1",
                        help="URL of the llama.cpp server")
    parser.add_argument("--model", type=str, default=None,
                        help="Model identifier (not used, kept for CLI consistency)")
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
