import base64

INVOICE_DETECTION_SCHEMA = {
    "type": "object",
    "properties": {
        "invoice": {
            "type": "boolean",
            "description": "Invoice or not"
        }
    },
    "required": ["invoice"],
    "additionalProperties": False
}

INVOICE_PROPERTIES_SCHEMA = {
    "type": "object",
    "properties": {
        "invoice_date": {
            "type": ["string", "null"],
            "description": "Date of the invoice in the format YYYY-MM-DD. Use null if the date is missing or unreadable."
        },
        "total_amount": {
            "type": ["number", "null"],
            "description": "Final total amount of the invoice as a number, e.g., 31496 or 31496.0. Use null if missing."
        },
        "currency": {
            "type": ["string", "null"],
            "description": "Currency of the invoice (prefer ISO code like EUR, USD, DEM). Use null if missing."
        }
    },
    "required": ["invoice_date", "total_amount", "currency"],
    "additionalProperties": False
}

INVOICE_DETECTION_PROMPT = "Is this image a photo of an invoice?"

INVOICE_PROPERTIES_PROMPT = """You are an OCR and information-extraction assistant for invoices.

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


def invoice_detection_response_format():
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "response",
            "strict": True,
            "schema": INVOICE_DETECTION_SCHEMA
        },
        "required": ["invoice"],
        "additionalProperties": False
    }


def invoice_properties_response_format():
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "invoice_schema",
            "strict": True,
            "schema": INVOICE_PROPERTIES_SCHEMA
        }
    }


def encode_image(image_path):
    """
    Encode an image file to base64 format.

    Args:
        image_path (str): Path to the image file.

    Returns:
        str: Base64 encoded image string.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')