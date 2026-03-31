import logging
import os

from parser import parse_classification
from providers.base import ImageClassificationProvider
from providers.prompt import CLASSIFICATION_PROMPT

logger = logging.getLogger(__name__)


class OpenAIProvider(ImageClassificationProvider):
    """Requires: pip install openai"""

    def __init__(self) -> None:
        from openai import OpenAI

        self.model = os.environ.get("OPENAI_MODEL", "gpt-4o")
        self.client = OpenAI()
        logger.info("Using OpenAI model: %s", self.model)

    async def classify_image(self, image_path: str) -> dict:
        data, mime_type = self.read_image(image_path)

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{data}"}},
                    {"type": "text", "text": CLASSIFICATION_PROMPT},
                ],
            }],
        )

        return parse_classification(response.choices[0].message.content)
