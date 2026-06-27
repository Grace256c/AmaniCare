"""User registration and profile API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user import UserRegisterResponse, UserResponse, UserCreate, UserUpdate
from app.services.registration_service import RegistrationService

router = APIRouter(prefix="/api/users", tags=["Users"])


def get_registration_service(db: AsyncSession = Depends(get_db)) -> RegistrationService:
    """Dependency injection for RegistrationService."""
    return RegistrationService(db)


@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    payload: UserCreate,
    service: RegistrationService = Depends(get_registration_service),
) -> UserRegisterResponse:
    """Register a new MamaCare AI user."""
    try:
        user = await service.register(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return UserRegisterResponse(user=UserResponse.model_validate(user))


@router.get("/{phone_number}", response_model=UserResponse)
async def get_user(
    phone_number: str,
    service: RegistrationService = Depends(get_registration_service),
) -> UserResponse:
    """Retrieve a registered user by phone number."""
    try:
        user = await service.get_user(phone_number)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(user)


@router.put("/{phone_number}", response_model=UserResponse)
async def update_user(
    phone_number: str,
    payload: UserUpdate,
    service: RegistrationService = Depends(get_registration_service),
) -> UserResponse:
    """Update an existing user profile."""
    try:
        user = await service.update_user(phone_number, payload)
    except ValueError as exc:
        status_code = status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc

    return UserResponse.model_validate(user)
