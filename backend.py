from enum import Enum
from openai import OpenAI
from os import getenv
from dotenv import load_dotenv
from base import BaseInferencer

load_dotenv()


class BackendType(Enum):
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    LLAMA = "llama"


class Backend(BaseInferencer):
    def __init__(
        self,
        type: BackendType,
        model: str = None,
        base_url: str = None,
        api_key: str = None
    ):
        self.type = type
        self.model = model

        if type == BackendType.LLAMA:
            self.client = OpenAI(
                base_url=base_url or "http://localhost:8080/v1",
                api_key=api_key or "not-needed"
            )
        elif type == BackendType.OLLAMA:
            self.client = OpenAI(
                base_url="http://localhost:11434/v1",
                api_key=getenv("OLLAMA_API_KEY")
            )
        else:
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=getenv("OPENROUTER_API_KEY")
            )

    def generate(self, prompt, image_path, response_format, model=None):
        effective_model = model or self.model
        if self.type == BackendType.LLAMA:
            effective_model = ""
        return super().generate(prompt, image_path, response_format, effective_model)
