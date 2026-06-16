from app.config.config import settings

def build_image_url(path: str) -> str:
    return f"{settings.BASE_URL}/{path}"