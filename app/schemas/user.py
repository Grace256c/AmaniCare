"""User Pydantic schemas."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.security import validate_age, validate_phone_number
from app.models.user import LifeStage


class UserBase(BaseModel):
    """Shared user fields."""

    phone_number: str = Field(..., examples=["+256700000000"])
    name: str = Field(..., min_length=1, max_length=100, examples=["Grace"])
    full_name: str | None = Field(default=None, max_length=150)
    date_of_birth: date | None = Field(default=None)
    age: int = Field(..., ge=10, le=120, examples=[23])
    district: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    life_stage: LifeStage = Field(..., examples=[LifeStage.REGULAR])
    language: str = Field(default="English", max_length=50, examples=["English"])
    sms_opt_in: bool = Field(default=False, examples=[True])
    voice_opt_in: bool = Field(default=False, examples=[True])
    whatsapp_opt_in: bool = Field(default=False, examples=[True])
    preferred_language: str = Field(default="English", max_length=50, examples=["English"])
    preferred_contact_time: str | None = Field(default=None, max_length=50)
    sms_opt_out_at: datetime | None = Field(default=None)
    last_sms_sent_at: datetime | None = Field(default=None)
    blood_group: str | None = Field(default=None, max_length=10)
    allergies: str | None = Field(default=None)
    chronic_conditions: str | None = Field(default=None)
    medications: str | None = Field(default=None)
    disabilities: str | None = Field(default=None)

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
    # lifecycle fields
    menarche_age: int | None = Field(default=None)
    currently_menstruating: bool | None = Field(default=None)
    cycle_regular: bool | None = Field(default=None)
    average_cycle_length: int | None = Field(default=None)
    average_period_length: int | None = Field(default=None)
    contraception_method: str | None = Field(default=None, max_length=100)
    trying_to_conceive: bool | None = Field(default=None)
    menopause_status: str | None = Field(default=None, max_length=50)
    pregnancy_history_count: int | None = Field(default=None)
    miscarriage_history_count: int | None = Field(default=None)
    c_section_history_count: int | None = Field(default=None)
    age_at_first_period: int | None = Field(default=None)
    symptom_patterns: str | None = Field(default=None)
    last_period_date: date | None = Field(default=None, description="YYYY-MM-DD")
    cycle_length: int | None = Field(default=None, description="Average cycle length in days")
    conception_date: date | None = Field(default=None, description="YYYY-MM-DD")
    estimated_due_date: date | None = Field(default=None, description="YYYY-MM-DD")
    pregnancy_week: int | None = Field(default=None)
    gestational_age: int | None = Field(default=None)
    trimester: str | None = Field(default=None, max_length=30)
    delivery_date: date | None = Field(default=None, description="YYYY-MM-DD")
    delivery_type: str | None = Field(default=None, max_length=50)
    breastfeeding_status: str | None = Field(default=None, max_length=50)
    symptom_preferences: str | None = Field(default=None)
    hot_flashes: bool | None = Field(default=None)
    sleep_changes: bool | None = Field(default=None)
    mood_changes: bool | None = Field(default=None)
    bone_health: bool | None = Field(default=None)
    night_sweats: bool | None = Field(default=None)
    menopause_preferences: str | None = Field(default=None, description="Comma-separated preferences")


class UserUpdate(BaseModel):
    """Schema for partial user updates."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    age: int | None = Field(default=None, ge=10, le=120)
    life_stage: LifeStage | None = None
    language: str | None = Field(default=None, max_length=50)
    sms_opt_in: bool | None = Field(default=None)
    voice_opt_in: bool | None = Field(default=None)
    whatsapp_opt_in: bool | None = Field(default=None)
    preferred_language: str | None = Field(default=None, max_length=50)
    preferred_contact_time: str | None = Field(default=None, max_length=50)
    sms_opt_out_at: datetime | None = Field(default=None)
    last_sms_sent_at: datetime | None = Field(default=None)
    blood_group: str | None = Field(default=None, max_length=10)
    allergies: str | None = Field(default=None)
    chronic_conditions: str | None = Field(default=None)
    medications: str | None = Field(default=None)
    disabilities: str | None = Field(default=None)
    menarche_age: int | None = Field(default=None)
    currently_menstruating: bool | None = Field(default=None)
    cycle_regular: bool | None = Field(default=None)
    average_cycle_length: int | None = Field(default=None)
    average_period_length: int | None = Field(default=None)
    contraception_method: str | None = Field(default=None, max_length=100)
    trying_to_conceive: bool | None = Field(default=None)
    menopause_status: str | None = Field(default=None, max_length=50)
    pregnancy_history_count: int | None = Field(default=None)
    miscarriage_history_count: int | None = Field(default=None)
    c_section_history_count: int | None = Field(default=None)
    age_at_first_period: int | None = Field(default=None)
    symptom_patterns: str | None = Field(default=None)
    last_period_date: date | None = Field(default=None)
    cycle_length: int | None = Field(default=None)
    conception_date: date | None = Field(default=None)
    estimated_due_date: date | None = Field(default=None)
    pregnancy_week: int | None = Field(default=None)
    gestational_age: int | None = Field(default=None)
    trimester: str | None = Field(default=None, max_length=30)
    delivery_date: date | None = Field(default=None)
    delivery_type: str | None = Field(default=None, max_length=50)
    breastfeeding_status: str | None = Field(default=None, max_length=50)
    symptom_preferences: str | None = Field(default=None)
    hot_flashes: bool | None = Field(default=None)
    sleep_changes: bool | None = Field(default=None)
    mood_changes: bool | None = Field(default=None)
    bone_health: bool | None = Field(default=None)
    night_sweats: bool | None = Field(default=None)
    menopause_preferences: str | None = Field(default=None)

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
    voice_opt_in: bool = False
    whatsapp_opt_in: bool = False
    preferred_language: str | None = None
    preferred_contact_time: str | None = None
    sms_opt_out_at: datetime | None = None
    last_sms_sent_at: datetime | None = None
    # lifecycle fields
    full_name: str | None = None
    date_of_birth: date | None = None
    district: str | None = None
    country: str | None = None
    blood_group: str | None = None
    allergies: str | None = None
    chronic_conditions: str | None = None
    medications: str | None = None
    disabilities: str | None = None
    menarche_age: int | None = None
    currently_menstruating: bool | None = None
    cycle_regular: bool | None = None
    average_cycle_length: int | None = None
    average_period_length: int | None = None
    contraception_method: str | None = None
    trying_to_conceive: bool | None = None
    menopause_status: str | None = None
    pregnancy_history_count: int | None = None
    miscarriage_history_count: int | None = None
    c_section_history_count: int | None = None
    age_at_first_period: int | None = None
    symptom_patterns: str | None = None
    last_period_date: date | None = None
    cycle_length: int | None = None
    fertile_window_start: date | None = None
    fertile_window_end: date | None = None
    conception_date: date | None = None
    estimated_due_date: date | None = None
    pregnancy_week: int | None = None
    gestational_age: int | None = None
    trimester: str | None = None
    delivery_date: date | None = None
    delivery_type: str | None = None
    breastfeeding_status: str | None = None
    postpartum_week: int | None = None
    symptom_preferences: str | None = None
    hot_flashes: bool | None = None
    sleep_changes: bool | None = None
    mood_changes: bool | None = None
    bone_health: bool | None = None
    night_sweats: bool | None = None
    menopause_preferences: str | None = None


class UserRegisterResponse(BaseModel):
    """Registration success wrapper."""

    success: bool = True
    user: UserResponse
