from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    gemini_api_key: str = ""
    # Verify against https://ai.google.dev/gemini-api/docs/models if you get a 404.
    gemini_model: str = "gemini-3.5-flash"
    app_name: str = "EduGenie"
    max_input_chars: int = 12000
    explanation_provider: str = "gemini"  # "gemini" or "local"

    # Thinking models spend part of this budget on reasoning, so keep it generous.
    max_output_tokens: int = 8192
    # None = use the model's default (recommended for Gemini 3 models).
    temperature: Optional[float] = None
    request_timeout_seconds: int = 60
    # Per-IP limit to protect your API quota. 0 disables it.
    rate_limit_per_minute: int = 30

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",  # always next to main.py, whatever the working directory
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
