import importlib
import logging
import os

from providers.base import ImageClassificationProvider

logger = logging.getLogger(__name__)

PROVIDERS: dict[str, str] = {
    "claude": "providers.claude_provider.ClaudeProvider",
    "openai": "providers.openai_provider.OpenAIProvider",
    "ollama": "providers.ollama_provider.OllamaProvider",
}

_cached_provider: ImageClassificationProvider | None = None


def get_provider() -> ImageClassificationProvider:
    """Return the provider set by MODEL_PROVIDER env var. Cached after first call."""
    global _cached_provider
    if _cached_provider is not None:
        return _cached_provider

    name = os.environ.get("MODEL_PROVIDER", "claude").lower()

    if name not in PROVIDERS:
        available = ", ".join(sorted(PROVIDERS))
        raise ValueError(f"Unknown MODEL_PROVIDER '{name}'. Available: {available}")

    module_path, class_name = PROVIDERS[name].rsplit(".", 1)
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    _cached_provider = cls()
    return _cached_provider
