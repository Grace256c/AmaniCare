"""Reminder ORM model for scheduled health notifications."""

import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ReminderType(str, enum.Enum):
    """Types of health reminders supported by the MVP."""

    PERIOD = "period"
    MEDICATION = "medication"
    PREGNANCY_CHECKIN = "pregnancy_checkin"
    MENOPAUSE_WELLNESS = "menopause_wellness"


class Reminder(Base):
    """Mock scheduled reminder for SMS notifications (future feature)."""

    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    reminder_type: Mapped[ReminderType] = mapped_column(Enum(ReminderType), nullable=False)
    next_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user = relationship("User", backref="reminders")
