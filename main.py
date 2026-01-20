from openrouter import Inferencer
from local import LocalLlama
import json

def workflow(Inferencer: Inferencer, image_path):
    invoice = Inferencer.invoice_or_not(image_path, "minicpm-v:8b-2.6-q4_K_M")

    print(invoice)

    if isinstance(invoice, str):
        # If invoice is a string, try to convert it to a dictionary
        try:
            invoice = json.loads(invoice)
        except json.JSONDecodeError:
            # If the string cannot be converted to a dictionary, handle the error
            print("Error: Could not convert invoice to a dictionary")
            return None

    if invoice.get("invoice"):
        return Inferencer.invoice_properties(image_path, "minicpm-v:8b-2.6-q4_K_M")
    else:
        print("Image is not an invoice.")
        return None

if __name__ == '__main__':

    ollama = Inferencer(local=True)

    img_path = f"./rvl_cdip_invoice_images/invoice_00001.png"
    properties = workflow(ollama, img_path)

    print(properties)