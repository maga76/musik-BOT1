"""
Конфигурация бота — загружает переменные окружения через pydantic-settings.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram
    BOT_TOKEN: str

    # OpenAI
    OPENAI_API_KEY: Optional[str] = None

    # Stability AI
    STABILITY_API_KEY: Optional[str] = None

    # ACRCloud
    ACRCLOUD_HOST: str = "identify-eu-west-1.acrcloud.com"
    ACRCLOUD_ACCESS_KEY: Optional[str] = None
    ACRCLOUD_ACCESS_SECRET: Optional[str] = None

    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/data/bot.db"

    # Admins
    ADMIN_IDS: list[int] = []

    # Rate limits
    RATE_LIMIT_IMAGE: int = 10
    RATE_LIMIT_MUSIC: int = 20
    RATE_LIMIT_RECOGNIZE: int = 15

    # Files
    MAX_FILE_SIZE_MB: int = 50

    # Logging
    LOG_LEVEL: str = "INFO"

    @field_validator("ADMIN_IDS", mode="before")
    @classmethod
    def parse_admin_ids(cls, v):
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v

    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @property
    def downloads_dir(self) -> Path:
        p = BASE_DIR / "downloads"
        p.mkdir(exist_ok=True)
        return p

    @property
    def logs_dir(self) -> Path:
        p = BASE_DIR / "logs"
        p.mkdir(exist_ok=True)
        return p


settings = Settings()
