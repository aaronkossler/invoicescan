from llama_cpp import Llama
from os import getenv
from dotenv import load_dotenv
from utils import encode_image

# Load environment variables from .env file
load_dotenv()

class LocalLlama:
    def __init__(self, model_path):
        self.llm = Llama(
            model_path=model_path,
            # IMPORTANT: point Python to your Vulkan-enabled llama.dll
            library_path=getenv("LLAMACPP_PATH"),
            n_gpu_layers=20,     # same as -ngl 20
            main_gpu=0,          # Vulkan0 = your AMD R9 390
            n_ctx=4096,          # same as -c 4096
            n_threads=10,        # same as -t 10
        )

    def generate(self, prompt, image_path=None, response_format=None):
        if not image_path:
            messages = [{"role": "user", "content": prompt}]
        else:
            image = encode_image(image_path)
            messages = [{"role": "user", "content": [{
                "type": "text",
                "text": prompt
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image}"
                }
            }]}]
        
        completion = self.llm.create_chat_completion(
            messages=messages
        )

        return completion["choices"][0]["message"]["content"]