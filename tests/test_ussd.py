"""USSD webhook tests."""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_ussd_welcome_menu(client: AsyncClient) -> None:
    """Empty USSD text should show the welcome menu."""
    response = await client.post(
        "/api/ussd",
        data={
            "sessionId": "session-001",
            "phoneNumber": "+256700000000",
            "text": "",
            "serviceCode": "*384*123#",
        },
    )
    assert response.status_code == 200
    assert response.text.startswith("CON ")
    assert "Welcome to MamaCare AI" in response.text
    assert "1 Register" in response.text


@pytest.mark.asyncio
async def test_ussd_registration_prompts_name(client: AsyncClient) -> None:
    """Selecting register should prompt for name."""
    response = await client.post(
        "/api/ussd",
        data={
            "sessionId": "session-002",
            "phoneNumber": "+256700000000",
            "text": "1",
            "serviceCode": "*384*123#",
        },
    )
    assert response.status_code == 200
    assert response.text.startswith("CON ")
    assert "Enter your name" in response.text


@pytest.mark.asyncio
async def test_ussd_health_question_flow(client: AsyncClient) -> None:
    """Registered users can ask health questions via USSD."""
    await client.post(
        "/api/users/register",
        json={
            "phone_number": "+256700000002",
            "name": "Sarah",
            "age": 30,
            "life_stage": "Regular",
            "language": "English",
        },
    )

    mock_advice = "Rest, hydrate, and seek care if symptoms worsen."

    with patch(
        "app.services.deepseek_service.DeepseekService.generate_advice",
        new=AsyncMock(return_value=mock_advice),
    ):
        response = await client.post(
            "/api/ussd",
            data={
                "sessionId": "session-003",
                "phoneNumber": "+256700000002",
                "text": "2*I have a headache",
                "serviceCode": "*384*123#",
            },
        )

    assert response.status_code == 200
    assert response.text.startswith("END ")
    assert mock_advice in response.text
