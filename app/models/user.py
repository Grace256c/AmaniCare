"""User ORM model."""

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, func
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
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    life_stage: Mapped[LifeStage] = mapped_column(Enum(LifeStage), nullable=False)
    language: Mapped[str] = mapped_column(String(50), default="English", nullable=False)
    sms_opt_in: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(50), default="English", nullable=False)
    sms_opt_out_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_sms_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    # lifecycle-specific fields
    last_period_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    cycle_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fertile_window_start: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    fertile_window_end: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    conception_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    estimated_due_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    pregnancy_week: Mapped[int | None] = mapped_column(Integer, nullable=True)
    delivery_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    postpartum_week: Mapped[int | None] = mapped_column(Integer, nullable=True)
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
