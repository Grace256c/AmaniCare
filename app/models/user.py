"""User ORM model."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

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
