from providers import get_provider


async def classify_image(image_path: str) -> dict:
    provider = get_provider()
    return await provider.classify_image(image_path)
