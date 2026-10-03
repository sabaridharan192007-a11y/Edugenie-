import pytest

import gemini_service
import main
from config import settings


@pytest.fixture(autouse=True)
def demo_mode(monkeypatch):
    """Every test runs offline, whatever is in your real .env file."""
    monkeypatch.setattr(settings, "gemini_api_key", "")
    monkeypatch.setattr(settings, "explanation_provider", "gemini")
    monkeypatch.setattr(settings, "rate_limit_per_minute", 0)
    monkeypatch.setattr(gemini_service, "_client", None)
    main.reset_rate_limiter()
