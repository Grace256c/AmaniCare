"""Africa's Talking SMS integration service."""

from __future__ import annotations

import httpx
from loguru import logger

from app.core.config import get_settings


class AfricaTalkingSMSService:
    """Send SMS messages through Africa's Talking."""

    def __init__(self) -> None:
        self.settings = get_settings()

    async def send_sms(self, phone_number: str, message: str) -> bool:
        """Send an SMS to a phone number and return success status."""
        if not self.settings.africas_talking_username or not self.settings.africas_talking_api_key:
            logger.warning("Africa's Talking credentials are not configured; skipping SMS send")
            return False

        payload = {
            "username": self.settings.africas_talking_username,
            "to": phone_number,
            "message": message,
        }
        if self.settings.africas_talking_sender_id:
            payload["from"] = self.settings.africas_talking_sender_id

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.settings.africas_talking_sms_url,
                    data=payload,
                    auth=(self.settings.africas_talking_username, self.settings.africas_talking_api_key),
                )
                if response.status_code >= 400:
                    logger.error(
                        "Africa's Talking SMS send failed with status {}: {}",
                        response.status_code,
                        response.text,
                    )
                    return False
        except httpx.HTTPError as exc:
            logger.exception("Africa's Talking SMS send failed: {}", exc)
            return False

        logger.info("Africa's Talking SMS sent to {}", phone_number)
        return True
