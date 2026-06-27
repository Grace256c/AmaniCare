"""Reproductive profile model for normalized lifelong health tracking."""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ReproductiveProfile(Base):
    """Tracks reproductive health across the user's lifetime."""

    __tablename__ = "reproductive_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    menarche_age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    currently_menstruating: Mapped[bool | None] = mapped_column(nullable=True)
    cycle_regular: Mapped[bool | None] = mapped_column(nullable=True)
    average_cycle_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    average_period_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    contraception_method: Mapped[str | None] = mapped_column(String(100), nullable=True)
    trying_to_conceive: Mapped[bool | None] = mapped_column(nullable=True)
    menopause_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    pregnancy_history_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    miscarriage_history_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    c_section_history_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    age_at_first_period: Mapped[int | None] = mapped_column(Integer, nullable=True)
    symptom_patterns: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_period_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    cycle_length: Mapped[int | None] = mapped_column(Integer, nullable=True)
    conception_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    estimated_due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    pregnancy_week: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gestational_age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    trimester: Mapped[str | None] = mapped_column(String(30), nullable=True)
    delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    delivery_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    breastfeeding_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    symptom_preferences: Mapped[str | None] = mapped_column(Text, nullable=True)
    hot_flashes: Mapped[bool | None] = mapped_column(nullable=True)
    sleep_changes: Mapped[bool | None] = mapped_column(nullable=True)
    mood_changes: Mapped[bool | None] = mapped_column(nullable=True)
    bone_health: Mapped[bool | None] = mapped_column(nullable=True)
    night_sweats: Mapped[bool | None] = mapped_column(nullable=True)
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

    user = relationship("User", backref="reproductive_profile", uselist=False)
