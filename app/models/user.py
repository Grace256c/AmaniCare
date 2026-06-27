"""User ORM model."""

import enum
from datetime import date, datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Date
from sqlalchemy import Text

from app.core.database import Base


class LifeStage(str, enum.Enum):
    """Women's health life stage categories."""

    TEEN = "Teen"
    REGULAR = "Regular"
    TRYING_TO_CONCEIVE = "TryingToConceive"
    PREGNANT = "Pregnant"
    POSTPARTUM = "Postpartum"
    PERIMENOPAUSE = "Perimenopause"
    MENOPAUSE = "Menopause"


class User(Base):
    """Registered MamaCare AI user profile."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reproductive_profile_id: Mapped[int | None] = mapped_column(ForeignKey("reproductive_profiles.id", ondelete="SET NULL"), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    life_stage: Mapped[LifeStage] = mapped_column(Enum(LifeStage), nullable=False)
    language: Mapped[str] = mapped_column(String(50), default="English", nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(50), default="English", nullable=False)
    sms_opt_in: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    voice_opt_in: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    whatsapp_opt_in: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sms_opt_out_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    preferred_contact_time: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_sms_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    blood_group: Mapped[str | None] = mapped_column(String(10), nullable=True)
    allergies: Mapped[str | None] = mapped_column(Text, nullable=True)
    chronic_conditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    medications: Mapped[str | None] = mapped_column(Text, nullable=True)
    disabilities: Mapped[str | None] = mapped_column(Text, nullable=True)
    # reproductive and lifecycle-specific fields
    menarche_age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    currently_menstruating: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    cycle_regular: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    average_cycle_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    average_period_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    contraception_method: Mapped[str | None] = mapped_column(String(100), nullable=True)
    trying_to_conceive: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    menopause_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    pregnancy_history_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    miscarriage_history_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    c_section_history_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    age_at_first_period: Mapped[int | None] = mapped_column(Integer, nullable=True)
    symptom_patterns: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_period_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    cycle_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fertile_window_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    fertile_window_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    conception_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    estimated_due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    pregnancy_week: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gestational_age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    trimester: Mapped[str | None] = mapped_column(String(30), nullable=True)
    delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    delivery_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    breastfeeding_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    postpartum_week: Mapped[int | None] = mapped_column(Integer, nullable=True)
    symptom_preferences: Mapped[str | None] = mapped_column(Text, nullable=True)
    hot_flashes: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    sleep_changes: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    mood_changes: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    bone_health: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    night_sweats: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    menopause_preferences: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
