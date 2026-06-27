"""AI advice endpoint tests."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


REGISTER_PAYLOAD = {
    "phone_number": "+256700000001",
    "name": "Amina",
    "age": 28,
    "life_stage": "Pregnant",
    "language": "English",
}


@pytest.mark.asyncio
async def test_advice_endpoint(client: AsyncClient) -> None:
    """POST /api/advice should return AI advice for a registered user."""
    await client.post("/api/users/register", json=REGISTER_PAYLOAD)

    mock_advice = (
        "Period pain can be normal, but if pain is severe or accompanied by "
        "heavy bleeding you should visit a nearby clinic."
    )

    with patch(
        "app.services.gemini_service.GeminiService.generate_advice",
        new=AsyncMock(return_value=mock_advice),
    ):
        response = await client.post(
            "/api/advice",
            json={
                "phone_number": REGISTER_PAYLOAD["phone_number"],
                "question": "I have severe period cramps.",
            },
        )

    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "I have severe period cramps."
    assert data["advice"] == mock_advice


@pytest.mark.asyncio
async def test_advice_user_not_found(client: AsyncClient) -> None:
    """POST /api/advice should 404 when user is not registered."""
    response = await client.post(
        "/api/advice",
        json={
            "phone_number": "+256788888888",
            "question": "I feel dizzy.",
        },
    )
    assert response.status_code == 404
    assert response.json()["success"] is False
