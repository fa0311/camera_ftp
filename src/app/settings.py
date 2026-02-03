from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    broker_url: str = "redis://localhost:6379/0"
    backend_url: str = "redis://localhost:6379/0"


settings = Settings()
