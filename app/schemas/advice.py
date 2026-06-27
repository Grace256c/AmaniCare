"""Advice Pydantic schemas."""

from pydantic import BaseModel, Field, field_validator

from app.core.security import validate_phone_number


class AdviceRequest(BaseModel):
    """Request body for AI health advice."""

    phone_number: str = Field(..., examples=["+256700000000"])
    question: str = Field(..., min_length=3, max_length=1000, examples=["I have severe period cramps."])

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return validate_phone_number(value)


class AdviceResponse(BaseModel):
    """AI-generated health advice response."""

    question: str
    advice: str
