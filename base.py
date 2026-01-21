import json
from utils import (
    encode_image,
    INVOICE_DETECTION_PROMPT,
    INVOICE_PROPERTIES_PROMPT,
    invoice_detection_response_format,
    invoice_properties_response_format
)


class BaseInferencer:
    def generate(self, prompt, image_path, response_format, model=None):
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
        # print(completion)
        return completion.choices[0].message.content

    def invoice_or_not(self, image_path, model=None):
        return self.generate(
            INVOICE_DETECTION_PROMPT,
            image_path,
            invoice_detection_response_format(),
            model
        )

    def invoice_properties(self, image_path, model=None):
        return self.generate(
            INVOICE_PROPERTIES_PROMPT,
            image_path,
            invoice_properties_response_format(),
            model
        )

    def process_invoice(self, image_path, model=None):
        result = self.invoice_or_not(image_path, model)
        # print(result)
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
