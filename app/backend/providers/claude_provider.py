import logging
import os

import anthropic

from parser import parse_classification
from providers.base import ImageClassificationProvider
from providers.prompt import CLASSIFICATION_PROMPT

logger = logging.getLogger(__name__)


class ClaudeProvider(ImageClassificationProvider):

    def __init__(self) -> None:
        self.model = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-20250514")
        self.client = anthropic.Anthropic()
        logger.info("Using Claude model: %s", self.model)

    async def classify_image(self, image_path: str) -> dict:
        data, mime_type = self.read_image(image_path)

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": mime_type, "data": data}},
                    {"type": "text", "text": CLASSIFICATION_PROMPT},
                ],
            }],
        )

        return parse_classification(message.content[0].text)
