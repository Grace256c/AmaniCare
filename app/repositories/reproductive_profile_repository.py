"""Repository for reproductive profile persistence."""

from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reproductive_profile import ReproductiveProfile


def _normalize_date(value: object | None) -> date | None:
    """Convert string/datetime dates to Python date objects."""
    if value is None or isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    return date.fromisoformat(str(value))


class ReproductiveProfileRepository:
    """Persist and manage reproductive profiles."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_user_id(self, user_id: int) -> ReproductiveProfile | None:
        """Fetch or create a reproductive profile for a user."""
        result = await self.db.execute(
            select(ReproductiveProfile).where(ReproductiveProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if profile is None:
            profile = ReproductiveProfile(user_id=user_id)
            self.db.add(profile)
            await self.db.flush()
            await self.db.refresh(profile)
        return profile

    async def create_or_get(self, user_id: int) -> ReproductiveProfile:
        """Ensure a profile exists for the user."""
        return await self.get_by_user_id(user_id)

    async def update(self, profile: ReproductiveProfile, **fields: object) -> ReproductiveProfile:
        """Update reproductive profile fields."""
        for key, value in fields.items():
            if value is None or not hasattr(profile, key):
                continue
            if key in {"conception_date", "estimated_due_date", "delivery_date", "last_period_date"}:
                setattr(profile, key, _normalize_date(value))
            else:
                setattr(profile, key, value)
        await self.db.flush()
        await self.db.refresh(profile)
        return profile
