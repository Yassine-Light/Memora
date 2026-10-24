"""Application configuration loaded from environment variables."""

from dataclasses import dataclass
from pathlib import Path
import os

ROOT_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "MemoryAnchor")
    environment: str = os.getenv("ENVIRONMENT", "development")
    database_path: Path = ROOT_DIR / os.getenv("DATABASE_PATH", "data/database.json")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY") or None
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemma-3-27b-it")
    scheduler_interval_seconds: int = int(
        os.getenv("SCHEDULER_INTERVAL_SECONDS", "30")
    )
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()

