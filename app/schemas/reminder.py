"""Reminder Pydantic schemas."""

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.security import validate_phone_number


class ReminderTypeSchema(str, Enum):
    """Reminder types exposed via the API."""

    PERIOD = "period"
    MEDICATION = "medication"
    PREGNANCY_CHECKIN = "pregnancy_checkin"
    MENOPAUSE_WELLNESS = "menopause_wellness"
    PERIOD_DUE = "period_due"
    FERTILE_WINDOW = "fertile_window"
    OVULATION = "ovulation"
    ANC_VISIT = "anc_visit"
    POSTNATAL_CHECK = "postnatal_check"
    WEEKLY_WELLNESS = "weekly_wellness"


class ReminderCreate(BaseModel):
    """Request to schedule a mock reminder."""

    phone_number: str = Field(..., examples=["+256700000000"])
    type: ReminderTypeSchema = Field(..., examples=[ReminderTypeSchema.PERIOD])
    next_date: date = Field(..., examples=["2026-07-15"])

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return validate_phone_number(value)


class ReminderResponse(BaseModel):
    """Scheduled reminder returned from the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    phone_number: str
    type: ReminderTypeSchema = Field(validation_alias="reminder_type")
    next_date: date
    created_at: datetime


class ReminderListResponse(BaseModel):
    """List of reminders for a user."""

    success: bool = True
    phone_number: str
    reminders: list[ReminderResponse]
