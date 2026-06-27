"""User data access layer."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import LifeStage, User


class UserRepository:
    """Repository for User CRUD operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_phone(self, phone_number: str) -> User | None:
        """Fetch a user by phone number."""
        result = await self.db.execute(
            select(User).where(User.phone_number == phone_number)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        *,
        phone_number: str,
        name: str,
        age: int,
        life_stage: LifeStage,
        language: str = "English",
    ) -> User:
        """Create a new user record."""
        user = User(
            phone_number=phone_number,
            name=name,
            age=age,
            life_stage=life_stage,
            language=language,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user: User, **fields: object) -> User:
        """Update mutable user fields."""
        for key, value in fields.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)
        await self.db.flush()
        await self.db.refresh(user)
        return user
