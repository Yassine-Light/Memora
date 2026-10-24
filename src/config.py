"""Application configuration loaded from environment variables."""

from dataclasses import dataclass
from pathlib import Path
import os

ROOT_DIR = Path(__file__).resolve().parent.parent
MODEL_ALIASES = {
    "gemma-2-2b-it": "gemma-4-26b-a4b-it",
    "gemma-4-2b-it": "gemma-4-26b-a4b-it",
}


def _load_local_env() -> None:
    """Load simple local .env values without overriding exported variables."""
    env_path = ROOT_DIR / ".env"
    if not env_path.is_file():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


_load_local_env()


def resolve_model_name(model_name: str) -> str:
    """Resolve a friendly local model name to an API-supported model ID."""
    return MODEL_ALIASES.get(model_name, model_name)


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "MemoryAnchor")
    environment: str = os.getenv("ENVIRONMENT", "development")
    database_path: Path = ROOT_DIR / os.getenv("DATABASE_PATH", "data/database.json")
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY") or None
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemma-4-26b-a4b-it")
    scheduler_interval_seconds: int = int(
        os.getenv("SCHEDULER_INTERVAL_SECONDS", "30")
    )
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
