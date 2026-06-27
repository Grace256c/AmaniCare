"""User Pydantic schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.security import validate_age, validate_phone_number
from app.models.user import LifeStage


class UserBase(BaseModel):
    """Shared user fields."""

    phone_number: str = Field(..., examples=["+256700000000"])
    name: str = Field(..., min_length=1, max_length=100, examples=["Grace"])
    age: int = Field(..., ge=10, le=120, examples=[23])
    life_stage: LifeStage = Field(..., examples=[LifeStage.REGULAR])
    language: str = Field(default="English", max_length=50, examples=["English"])
    sms_opt_in: bool = Field(default=False, examples=[True])
    preferred_language: str = Field(default="English", max_length=50, examples=["English"])
    sms_opt_out_at: datetime | None = Field(default=None)
    last_sms_sent_at: datetime | None = Field(default=None)

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return validate_phone_number(value)

    @field_validator("age")
    @classmethod
    def validate_user_age(cls, value: int) -> int:
        return validate_age(value)


class UserCreate(UserBase):
    """Schema for user registration."""
    sms_opt_in: bool = Field(default=False, description="Whether the user opts in to SMS")
    preferred_language: str | None = Field(default=None, max_length=50)


class UserUpdate(BaseModel):
    """Schema for partial user updates."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    age: int | None = Field(default=None, ge=10, le=120)
    life_stage: LifeStage | None = None
    language: str | None = Field(default=None, max_length=50)
    sms_opt_in: bool | None = Field(default=None)
    preferred_language: str | None = Field(default=None, max_length=50)
    sms_opt_out_at: datetime | None = Field(default=None)
    last_sms_sent_at: datetime | None = Field(default=None)

    @field_validator("age")
    @classmethod
    def validate_user_age(cls, value: int | None) -> int | None:
        if value is None:
            return value
        return validate_age(value)


class UserResponse(UserBase):
    """User data returned from the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    sms_opt_in: bool = False
    preferred_language: str | None = None
    sms_opt_out_at: datetime | None = None
    last_sms_sent_at: datetime | None = None


class UserRegisterResponse(BaseModel):
    """Registration success wrapper."""

    success: bool = True
    user: UserResponse
