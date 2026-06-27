"""SMS demo and opt-out API routes."""

from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.core.database import get_db
from app.schemas.user import UserUpdate
from app.services.registration_service import RegistrationService
from app.services.sms_service import AfricaTalkingSMSService
from app.repositories.sms_message_repository import SMSMessageRepository
from app.repositories.user_repository import UserRepository


router = APIRouter(prefix="/api/sms", tags=["SMS"])


def get_registration_service(db: AsyncSession = Depends(get_db)) -> RegistrationService:
    """Dependency injection for registration service."""
    return RegistrationService(db)


@router.post("/test")
async def send_test_sms(
    payload: dict[str, str],
    db: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    """Send a simple demo SMS using the existing Africa's Talking service."""
    phone_number = payload.get("phone_number", "")
    message = payload.get("message", "")
    if not phone_number or not message:
        raise HTTPException(status_code=400, detail="phone_number and message are required")

    service = AfricaTalkingSMSService()
    sms_repo = SMSMessageRepository(db)
    await sms_repo.log_message(phone_number=phone_number, message_body=message, direction="outbound", template_name="test")
    sent = await service.send_sms(phone_number, message)
    await sms_repo.update((await sms_repo.log_message(phone_number=phone_number, message_body=message, direction="outbound", template_name="test")), status=("sent" if sent else "failed"))
    return {"success": sent, "message": "Test SMS sent" if sent else "Test SMS skipped or failed"}


@router.post("/inbound")
async def inbound_sms(from_number: str = Form(...), text: str = Form(...), db: AsyncSession = Depends(get_db)):
    """Handle inbound SMS callbacks from Africa's Talking. Supports STOP opt-out."""
    phone = from_number
    user_repo = UserRepository(db)
    sms_repo = SMSMessageRepository(db)

    # log inbound
    await sms_repo.log_message(phone_number=phone, message_body=text, direction="inbound")

    if text.strip().lower() == "stop":
        user = await user_repo.get_by_phone(phone)
        if user:
            await user_repo.update(user, sms_opt_in=False, sms_opt_out_at=datetime.now(timezone.utc))
        return JSONResponse({"message": "opted_out"})

    return JSONResponse({"message": "received"})


@router.post("/opt-out")
async def opt_out_sms(
    payload: dict[str, str],
    service: RegistrationService = Depends(get_registration_service),
) -> dict[str, object]:
    """Disable SMS for a user when they reply STOP or call the API."""
    phone_number = payload.get("phone_number", "")
    if not phone_number:
        raise HTTPException(status_code=400, detail="phone_number is required")

    user = await service.get_user(phone_number)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    updated = await service.update_user(
        phone_number,
        UserUpdate(
            sms_opt_in=False,
            sms_opt_out_at=datetime.now(timezone.utc),
        ),
    )
    return {"success": True, "sms_opt_in": updated.sms_opt_in}
