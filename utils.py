import base64

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