"""User registration business logic."""

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import validate_phone_number
from app.models.user import LifeStage, User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class RegistrationService:
    """Handles user registration and profile updates."""

    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)

    async def register(self, data: UserCreate) -> User:
        """
        Register a new user or raise if phone number already exists.

        Raises:
            ValueError: When the phone number is already registered.
        """
        phone = validate_phone_number(data.phone_number)
        existing = await self.repo.get_by_phone(phone)
        if existing:
            raise ValueError("User with this phone number already exists")

        user = await self.repo.create(
            phone_number=phone,
            name=data.name.strip(),
            age=data.age,
            life_stage=data.life_stage,
            language=data.language.strip(),
            sms_opt_in=data.sms_opt_in,
            preferred_language=data.preferred_language.strip(),
        )
        logger.info("User registered: {} ({})", user.name, user.phone_number)
        return user

    async def get_user(self, phone_number: str) -> User | None:
        """Retrieve a user by phone number."""
        phone = validate_phone_number(phone_number)
        return await self.repo.get_by_phone(phone)

    async def update_user(self, phone_number: str, data: UserUpdate) -> User:
        """
        Update an existing user profile.

        Raises:
            ValueError: When the user is not found or no fields are provided.
        """
        phone = validate_phone_number(phone_number)
        user = await self.repo.get_by_phone(phone)
        if not user:
            raise ValueError("User not found")

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise ValueError("No fields provided for update")

        updated = await self.repo.update(user, **update_data)
        logger.info("User updated: {}", updated.phone_number)
        return updated

    async def register_from_ussd(
        self,
        *,
        phone_number: str,
        name: str,
        age: int,
        life_stage: LifeStage,
        language: str = "English",
        sms_opt_in: bool = False,
        preferred_language: str = "English",
    ) -> User:
        """Register or update a user from the USSD flow."""
        existing = await self.repo.get_by_phone(phone_number)
        if existing:
            return await self.repo.update(
                existing,
                name=name,
                age=age,
                life_stage=life_stage,
                language=language,
                sms_opt_in=sms_opt_in,
                preferred_language=preferred_language,
            )

        return await self.repo.create(
            phone_number=phone_number,
            name=name,
            age=age,
            life_stage=life_stage,
            language=language,
            sms_opt_in=sms_opt_in,
            preferred_language=preferred_language,
        )
