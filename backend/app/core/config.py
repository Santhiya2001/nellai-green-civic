import json
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENVIRONMENT: str = "development"
    TESTING: bool = False
    PROJECT_NAME: str = "Nellai Green & Civic"
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: str = '["http://localhost:5173"]'

    DATABASE_URL: str = "postgresql+asyncpg://nellai:nellai@localhost:5432/nellai_green_civic"

    JWT_SECRET_KEY: str = "insecure-dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14

    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_PATH: str = "/app/uploads"
    MAX_UPLOAD_SIZE_MB: int = 8
    ALLOWED_IMAGE_MIME_TYPES: str = "image/jpeg,image/png,image/webp"

    S3_ENDPOINT_URL: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_BUCKET_NAME: str = ""

    AI_SERVICE_URL: str = "http://ai-service:8100"
    AI_SERVICE_ENABLED: bool = True
    AI_SERVICE_TIMEOUT_SECONDS: int = 15

    NOTIFICATIONS_ENABLED: bool = True
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@nellaigreencivic.org"
    SMTP_USE_TLS: bool = True
    FCM_SERVER_KEY: str = ""

    # Every newly filed complaint sends a one-line alert email here, in
    # addition to the normal in-app notification to the reporter/authority.
    # Blank disables the alert (e.g. in CI/tests) without touching SMTP config.
    ADMIN_ALERT_EMAIL: str = ""

    REDIS_URL: str = "redis://localhost:6379/0"
    RATE_LIMIT_PER_MINUTE: int = 60

    DEFAULT_WORKING_DAYS_DEADLINE: int = 3
    DEFAULT_TIMEZONE: str = "Asia/Kolkata"

    @property
    def cors_origins(self) -> List[str]:
        try:
            return json.loads(self.BACKEND_CORS_ORIGINS)
        except json.JSONDecodeError:
            return [self.BACKEND_CORS_ORIGINS]

    @property
    def allowed_image_mime_types(self) -> List[str]:
        return [m.strip() for m in self.ALLOWED_IMAGE_MIME_TYPES.split(",") if m.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
