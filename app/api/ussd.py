"""USSD webhook API routes."""

from fastapi import APIRouter, Depends, Form
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.ussd_service import USSDService

router = APIRouter(prefix="/api/ussd", tags=["USSD"])


def get_ussd_service(db: AsyncSession = Depends(get_db)) -> USSDService:
    """Dependency injection for USSDService."""
    return USSDService(db)


@router.post("", response_class=PlainTextResponse)
async def ussd_callback(
    sessionId: str = Form(...),
    phoneNumber: str = Form(...),
    text: str = Form(default=""),
    serviceCode: str = Form(default=""),
    service: USSDService = Depends(get_ussd_service),
) -> PlainTextResponse:
    """
    Africa's Talking USSD webhook endpoint.

    Accepts form-encoded POST data and returns plain-text CON/END responses.
    """
    response_text = await service.handle(
        session_id=sessionId,
        phone_number=phoneNumber,
        text=text,
    )
    return PlainTextResponse(content=response_text, media_type="text/plain")
