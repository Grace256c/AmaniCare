"""USSD session ORM model for multi-step menu state."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class USSDFlow(str, enum.Enum):
    """Active USSD menu flow."""

    MAIN = "main"
    REGISTER_NAME = "register_name"
    REGISTER_AGE = "register_age"
    REGISTER_LIFE_STAGE = "register_life_stage"
    ASK_QUESTION = "ask_question"


class USSDSession(Base):
    """Tracks USSD session state across chained requests."""

    __tablename__ = "ussd_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    flow: Mapped[USSDFlow] = mapped_column(Enum(USSDFlow), default=USSDFlow.MAIN, nullable=False)
    # Temporary registration data stored between USSD steps.
    temp_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    temp_age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    temp_life_stage: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_input: Mapped[str | None] = mapped_column(Text, nullable=True)
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
