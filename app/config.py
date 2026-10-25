from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import json

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/darkmirror"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/darkmirror"
    SECRET_KEY: str = "darkmirror-secret-key-for-local-research-prototype"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""
    MODEL_NAME: str = "gpt-3.5-turbo"
    CORS_ORIGINS: str = '["http://localhost:3000","http://localhost:5173","http://localhost:5174"]'
    # Redis configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    # Report storage path (local or S3/GCS URI)
    REPORT_STORAGE_PATH: str = "./reports"
    # Pipeline model version tracking
    PIPELINE_VERSION: str = "1.0.0"

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.CORS_ORIGINS)

    model_config = SettingsConfigDict(env_file=(".env", "../.env"), env_file_encoding="utf-8", extra='ignore')

settings = Settings()
