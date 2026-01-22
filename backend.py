from enum import Enum
from openai import OpenAI
from os import getenv
from dotenv import load_dotenv
from base import BaseInferencer

load_dotenv()


class BackendType(Enum):
    """Enum representing available inference backends."""
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    LLAMA = "llama"


class Backend(BaseInferencer):
    """
    Unified backend for invoice processing.

    Supports OpenRouter API, Ollama, and llama.cpp server backends.
    Automatically creates an OpenAI-compatible client based on the backend type.

    Args:
        type: The backend type to use (OPENROUTER, OLLAMA, or LLAMA)
        model: Model identifier for OpenRouter/Ollama backends
        base_url: Custom server URL (defaults to LLAMA_SERVER_URL env var for LLAMA backend)
        api_key: Custom API key (defaults to environment variables)

    Attributes:
        type: The selected backend type
        model: The model identifier (if applicable)
        client: OpenAI-compatible client instance
    """

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
                base_url=base_url or getenv("LLAMA_SERVER_URL", "http://localhost:8080/v1"),
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
        """
        Generate completion with model-aware handling.

        Llama.cpp server requires empty model string, while other backends
        use the provided model identifier.

        Args:
            prompt: Text prompt for the model
            image_path: Path to image file
            response_format: OpenAI response format specification
            model: Override model identifier (optional)

        Returns:
            str: Model response content
        """
        effective_model = model or self.model
        if self.type == BackendType.LLAMA:
            effective_model = ""
        return super().generate(prompt, image_path, response_format, effective_model)
