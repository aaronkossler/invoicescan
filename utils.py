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