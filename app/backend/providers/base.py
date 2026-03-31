import base64
import mimetypes
from abc import ABC, abstractmethod

SUPPORTED_MIME_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
DEFAULT_MIME_TYPE = "image/jpeg"


class ImageClassificationProvider(ABC):
    """Interface for image classification backends.

    Subclass this and implement classify_image() to add a new provider.
    Register it in providers/factory.py.
    """

    @abstractmethod
    async def classify_image(self, image_path: str) -> dict:
        ...

    @staticmethod
    def read_image(image_path: str) -> tuple[str, str]:
        """Read image file, return (base64_data, mime_type)."""
        with open(image_path, "rb") as f:
            data = base64.standard_b64encode(f.read()).decode("utf-8")

        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type not in SUPPORTED_MIME_TYPES:
            mime_type = DEFAULT_MIME_TYPE

        return data, mime_type
