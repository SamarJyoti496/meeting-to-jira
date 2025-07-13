from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # App settings
    APP_NAME: str = "Meeting to Jira System"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/meeting_jira"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # API Keys
    OPENAI_API_KEY: str
    GEMINI_API_KEY: str
    JIRA_SERVER: str
    JIRA_EMAIL: str
    JIRA_API_TOKEN: str

    # File storage
    UPLOAD_DIR: str = "app/static/uploads"
    MAX_FILE_SIZE: int = 500 * 1024 * 1024  # 500MB

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Audio processing
    SUPPORTED_FORMATS: list = ["mp3", "wav", "mp4", "m4a", "webm"]

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), ".env")

settings = Settings()