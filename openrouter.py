from openai import OpenAI
from os import getenv
from dotenv import load_dotenv
from utils import encode_image

# Load environment variables from .env file
load_dotenv()

# Free limit: If you are using a free model variant (with an ID ending in :free), then you will be limited to 20 requests per minute and 200 requests per day.

class Inferencer:
    def __init__(self, local):
        if local:
            base_url="http://localhost:11434/v1"
            api_key=getenv("OLLAMA_API_KEY")
        else:
            base_url="https://openrouter.ai/api/v1"
            api_key=getenv("OPENROUTER_API_KEY")
        
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )

    def generate(self, prompt, image_path, response_format, model):
        """
        Generate a completion given the system prompt, user prompt, and image url.

        Args:
            system (str): The system prompt.
            prompt (str): The user prompt.
            image_path (str): The path to the image file.
            model (str): The model to use for generation. Defaults to "google/gemma-3-27b-it:free".

        Returns:
            str: The generated completion.
        """
        image = encode_image(image_path)
        completion = self.client.chat.completions.create(
            model=model,
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
                }}]
            }],
            response_format=response_format,
            temperature=0
            )
        # print(completion)
        return completion.choices[0].message.content

    def invoice_or_not(self, image_path, model):
        """
        Checks if the given image is a photo of an invoice.

        Args:
            image_path (str): The path to the image file.

        Returns:
            dict: A dictionary containing the result of the check, where the key is "invoice" and the value is a boolean indicating whether the image is an invoice or not.
        """
        prompt = "Is this image a photo of an invoice?"
        response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "response",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "invoice": {
                                "type": "boolean",
                                "description": "Invoice or not"
                            }
                        }
                    }
                },
                "required": ["invoice"],
                "additionalProperties": False
            }
        return self.generate(prompt, image_path, response_format, model)

    def invoice_properties(self, image_path, model):
        """
        Generates a dictionary containing the properties of the invoice from the given image path.

        Args:
            image_path (str): The path to the image file.

        Returns:
            dict: A dictionary containing the properties of the invoice, where the keys are "invoice_date", "total_amount", and "currency", and the values are the corresponding values for each property.
        """

        prompt = """
        You are an OCR and information-extraction assistant for invoices.

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
        Return only valid JSON, no markdown, no comments.
        """

        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "invoice_schema",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "invoice_date": {
                            "type": ["string", "null"],
                            "description": (
                                "Date of the invoice in the format YYYY-MM-DD. "
                                # "Must match ^\\d{4}-\\d{2}-\\d{2}$. "
                                "Use null if the date is missing or unreadable."
                            ),
                            # "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
                        },
                        "total_amount": {
                            "type": ["number", "null"],
                            "description": (
                                "Final total amount of the invoice as a number, "
                                "e.g., 31496 or 31496.0. Use null if missing."
                            )
                        },
                        "currency": {
                            "type": ["string", "null"],
                            "description": (
                                "Currency of the invoice (prefer ISO code like EUR, USD, DEM). "
                                "Use null if missing."
                            )
                        }
                    },
                    "required": ["invoice_date", "total_amount", "currency"],
                    "additionalProperties": False
                }
            }
        }

        return self.generate(prompt, image_path, response_format, model)