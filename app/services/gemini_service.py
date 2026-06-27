"""Google Gemini integration for health advice generation."""

import httpx
from loguru import logger

from app.core.config import get_settings
from app.models.user import User
from app.utils.prompts import build_prompt


class GeminiService:
    """Service wrapper for the Google Gemini generative AI API."""

    GEMINI_API_URL = (
        "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    )

    def __init__(self) -> None:
        self.settings = get_settings()

    async def generate_advice(self, user: User, question: str) -> str:
        """
        Send a personalized health question to Gemini and return advice text.

        Raises:
            ValueError: When API key is missing or response is empty.
            httpx.HTTPError: When the Gemini API request fails.
        """
        if not self.settings.google_api_key:
            logger.error("Gemini API key is not configured")
            raise ValueError("Gemini API key is not configured")

        prompt = build_prompt(user, question)
        url = self.GEMINI_API_URL.format(model=self.settings.gemini_model)
        params = {"key": self.settings.google_api_key}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 300,
            },
        }

        logger.info(
            "Sending Gemini request for user {} (life_stage={})",
            user.phone_number,
            user.life_stage.value,
        )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, params=params, json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            logger.error("Gemini API request failed: {}", exc)
            raise

        try:
            advice = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError, TypeError) as exc:
            logger.error("Unexpected Gemini response format: {}", data)
            raise ValueError("Failed to parse Gemini response") from exc

        logger.info("Gemini advice generated successfully for {}", user.phone_number)
        return advice
