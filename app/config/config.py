import os

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL")
    secret_key: str = os.getenv("SECRET_KEY")
    algorithm: str = os.getenv("ALGORITHM")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    login_max_attempts: int = int(os.getenv("MAX_ATTEMPTS"))
    rate_block_time: int = int(os.getenv("BLOCK_TIME"))
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR")
    TEMP_DIR: str = os.getenv("TEMP_DIR")
    BASE_URL: str = os.getenv("BASE_URL")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    SENDER_EMAIL: str = os.getenv("EMAIL_USER")
    SENDER_EMAIL_PASSWORD: str = os.getenv("EMAIL_PASS")


settings = Settings()
