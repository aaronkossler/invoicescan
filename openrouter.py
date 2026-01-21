from openai import OpenAI
from os import getenv
from dotenv import load_dotenv
from base import BaseInferencer

load_dotenv()


class Inferencer(BaseInferencer):
    def __init__(self, local=False):
        if local:
            base_url = "http://localhost:11434/v1"
            api_key = getenv("OLLAMA_API_KEY")
        else:
            base_url = "https://openrouter.ai/api/v1"
            api_key = getenv("OPENROUTER_API_KEY")

        self.client = OpenAI(base_url=base_url, api_key=api_key)
