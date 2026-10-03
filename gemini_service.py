import json
import logging
from typing import Type, TypeVar

from pydantic import BaseModel

from config import settings

logger = logging.getLogger("edugenie")

T = TypeVar("T", bound=BaseModel)

_client = None


class AIServiceError(RuntimeError):
    """An error whose message is safe to show to the end user."""


def get_client():
    """Return a Gemini client, or None when no API key is set (demo mode)."""
    global _client
    if not settings.gemini_api_key:
        return None
    if _client is None:
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise AIServiceError(
                "The google-genai package is not installed. Run: pip install -r requirements.txt"
            ) from exc
        _client = genai.Client(
            api_key=settings.gemini_api_key,
            http_options=types.HttpOptions(timeout=settings.request_timeout_seconds * 1000),
        )
    return _client


def _friendly_error(exc: Exception) -> AIServiceError:
    """Translate SDK errors into messages that help without leaking internals."""
    code = getattr(exc, "code", None)
    if code in (401, 403):
        msg = "The Gemini API key was rejected. Check GEMINI_API_KEY in your .env file."
    elif code == 404:
        msg = f"Gemini model '{settings.gemini_model}' was not found. Check GEMINI_MODEL in your .env file."
    elif code == 429:
        msg = "The Gemini quota or rate limit was reached. Please wait a moment and try again."
    elif code in (500, 502, 503, 504):
        msg = "Gemini is temporarily unavailable. Please try again shortly."
    elif "timeout" in type(exc).__name__.lower() or "timed out" in str(exc).lower():
        msg = "Gemini took too long to respond. Please try again."
    else:
        msg = "The AI service returned an error. Please try again."
    return AIServiceError(msg)


def _config(**extra):
    from google.genai import types

    if settings.temperature is not None:
        extra["temperature"] = settings.temperature
    return types.GenerateContentConfig(max_output_tokens=settings.max_output_tokens, **extra)


def _generate(prompt: str, **config_extra) -> str:
    client = get_client()
    if client is None:
        raise AIServiceError("Gemini API key is not configured.")
    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=_config(**config_extra),
        )
        text = response.text
    except AIServiceError:
        raise
    except Exception as exc:
        logger.exception("Gemini request failed")
        raise _friendly_error(exc) from exc
    if not text or not text.strip():
        raise AIServiceError(
            "Gemini returned an empty response (it may have been blocked by a safety filter). "
            "Try rephrasing your input."
        )
    return text.strip()


def generate_text(prompt: str) -> str:
    return _generate(prompt)


def generate_structured(prompt: str, schema: Type[T], attempts: int = 2) -> T:
    last_error: Exception | None = None
    for _ in range(attempts):
        text = _generate(
            prompt,
            response_mime_type="application/json",
            response_schema=schema,
        )
        try:
            return schema.model_validate(json.loads(text))
        except Exception as exc:  # malformed JSON or failed validation -> retry once
            logger.warning("Structured response failed validation: %s", exc)
            last_error = exc
    raise AIServiceError("The AI returned an invalid quiz format. Please try again.") from last_error
