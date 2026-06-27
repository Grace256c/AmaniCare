"""Deepseek integration for health advice generation."""

import httpx
from loguru import logger

from app.core.config import get_settings
from app.models.user import User
from app.utils.prompts import build_prompt


class DeepseekService:
    """Service wrapper for the Deepseek generative AI API."""

    def __init__(self) -> None:
        self.settings = get_settings()

    async def generate_advice(self, user: User, question: str) -> str:
        """Send a personalized health question to Deepseek and return advice text."""
        if not self.settings.deepseek_api_key:
            logger.error("Deepseek API key is not configured")
            raise ValueError("Deepseek API key is not configured")

        prompt = build_prompt(user, question)
        url = self.settings.deepseek_api_url
        payload: dict[str, object] = {
            "model": self.settings.deepseek_model,
            "input": prompt,
            "temperature": 0.7,
            "max_output_tokens": 300,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.deepseek_api_key}",
            "Content-Type": "application/json",
        }

        logger.info(
            "Sending Deepseek request for user {} (life_stage={}) to {}",
            user.phone_number,
            user.life_stage.value,
            url,
        )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            logger.error("Deepseek API request failed: {}", exc)
            raise

        advice = self._parse_response(data)
        if not advice:
            logger.error("Unexpected Deepseek response format: {}", data)
            raise ValueError("Failed to parse Deepseek response")

        logger.info("Deepseek advice generated successfully for {}", user.phone_number)
        return advice

    def _parse_response(self, data: object) -> str:
        if not isinstance(data, dict):
            return ""

        if text := self._extract_string(data, "response"):
            return text
        if text := self._extract_string(data, "output"):
            return text
        if choices := data.get("choices"):
            if isinstance(choices, list) and choices:
                first = choices[0]
                if isinstance(first, dict):
                    if text := self._extract_string(first, "text"):
                        return text
                    message = first.get("message")
                    if isinstance(message, dict) and (text := self._extract_string(message, "content")):
                        return text
        if outputs := data.get("outputs"):
            if isinstance(outputs, list) and outputs:
                first = outputs[0]
                if isinstance(first, dict):
                    if text := self._extract_string(first, "text"):
                        return text
                    content = first.get("content")
                    if isinstance(content, list) and content:
                        first_content = content[0]
                        if isinstance(first_content, dict) and (text := self._extract_string(first_content, "text")):
                            return text
                        if isinstance(first_content, str):
                            return first_content.strip()
        if candidates := data.get("candidates"):
            if isinstance(candidates, list) and candidates:
                first = candidates[0]
                if isinstance(first, dict):
                    content = first.get("content")
                    if isinstance(content, dict):
                        parts = content.get("parts")
                        if isinstance(parts, list) and parts:
                            first_part = parts[0]
                            if isinstance(first_part, dict) and (text := self._extract_string(first_part, "text")):
                                return text
                        if isinstance(content, str):
                            return content.strip()
        return ""

    @staticmethod
    def _extract_string(payload: object, key: str) -> str | None:
        if isinstance(payload, dict):
            value = payload.get(key)
            if isinstance(value, str):
                return value.strip()
        return None
