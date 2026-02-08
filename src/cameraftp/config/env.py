from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Env(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CAMERAFTP_", extra="ignore")
    config_path: Path = Path("configs/config.jsonc")
    log_level: str = "INFO"
