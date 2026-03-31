import logging
import os

import httpx

from parser import parse_classification
from providers.base import ImageClassificationProvider
from providers.prompt import CLASSIFICATION_PROMPT

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 120.0


class OllamaProvider(ImageClassificationProvider):
    """Connects to a local Ollama server. No extra pip deps needed (uses httpx)."""

    def __init__(self) -> None:
        self.host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.model = os.environ.get("OLLAMA_MODEL", "llava")
        logger.info("Using Ollama model: %s at %s", self.model, self.host)

    async def classify_image(self, image_path: str) -> dict:
        data, _ = self.read_image(image_path)

        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": CLASSIFICATION_PROMPT,
                    "images": [data],
                    "stream": False,
                },
            )
            response.raise_for_status()

        return parse_classification(response.json()["response"])
