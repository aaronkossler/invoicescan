import json
from typing import Optional
from utils import (
    encode_image,
    INVOICE_DETECTION_PROMPT,
    INVOICE_PROPERTIES_PROMPT,
    invoice_detection_response_format,
    invoice_properties_response_format
)


class BaseInferencer:
    """
    Base class for invoice processing inference.

    Provides shared methods for invoice detection and data extraction.
    Subclasses must implement client initialization (see Backend).

    Attributes:
        client: OpenAI-compatible client for LLM calls
    """

    def generate(self, prompt: str, image_path: str, response_format: dict, model: Optional[str] = None) -> str:
        """
        Generate completion via LLM with image support.

        Encodes the image to base64 and sends a multimodal request
        to the LLM with the specified response format for structured output.

        Args:
            prompt: Text prompt for the model
            image_path: Path to image file
            response_format: OpenAI response format specification
            model: Model identifier (optional, defaults to empty string)

        Returns:
            str: Model response content as JSON string
        """
        image = encode_image(image_path)
        completion = self.client.chat.completions.create(
            model=model or "",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image}"}}
                ]
            }],
            response_format=response_format,
            temperature=0
        )
        return completion.choices[0].message.content

    def invoice_or_not(self, image_path: str, model: Optional[str] = None) -> str:
        """
        Check if an image is an invoice.

        Uses a simple classification prompt to determine if the image
        contains an invoice.

        Args:
            image_path: Path to the image file
            model: Model identifier (optional)

        Returns:
            str: JSON string with {"invoice": boolean}
        """
        return self.generate(
            INVOICE_DETECTION_PROMPT,
            image_path,
            invoice_detection_response_format(),
            model
        )

    def invoice_properties(self, image_path: str, model: Optional[str] = None) -> str:
        """
        Extract structured data from an invoice image.

        Performs OCR and information extraction to get invoice date,
        total amount, and currency.

        Args:
            image_path: Path to the invoice image
            model: Model identifier (optional)

        Returns:
            str: JSON string with invoice_date, total_amount, and currency
        """
        return self.generate(
            INVOICE_PROPERTIES_PROMPT,
            image_path,
            invoice_properties_response_format(),
            model
        )

    def process_invoice(self, image_path: str, model: Optional[str] = None) -> Optional[str]:
        """
        Process an invoice image end-to-end.

        First checks if the image is an invoice, then extracts properties
        if it is. Returns None for non-invoice images.

        Args:
            image_path: Path to the image file
            model: Model identifier (optional)

        Returns:
            str: JSON string with extracted data, or None if not an invoice
        """
        result = self.invoice_or_not(image_path, model)

        if isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                print("Error: Could not parse invoice detection response")
                return None

        if result.get("invoice"):
            return self.invoice_properties(image_path, model)
        else:
            print("Image is not an invoice.")
            return None
