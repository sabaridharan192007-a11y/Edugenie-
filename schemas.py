from pydantic import BaseModel, Field, field_validator

from config import settings


class InputRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Topic, question, or passage")

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Input cannot be empty.")
        if len(value) > settings.max_input_chars:
            raise ValueError(f"Input is too long. Maximum is {settings.max_input_chars} characters.")
        return value
