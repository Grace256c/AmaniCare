"""User registration and profile tests."""

import pytest
from httpx import AsyncClient


REGISTER_PAYLOAD = {
    "phone_number": "+256700000000",
    "name": "Grace",
    "age": 23,
    "life_stage": "Regular",
    "language": "English",
}


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient) -> None:
    """POST /api/users/register should create a new user."""
    response = await client.post("/api/users/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["user"]["phone_number"] == REGISTER_PAYLOAD["phone_number"]
    assert data["user"]["name"] == "Grace"
    assert data["user"]["life_stage"] == "Regular"


@pytest.mark.asyncio
async def test_register_duplicate_user(client: AsyncClient) -> None:
    """Registering the same phone number twice should fail."""
    await client.post("/api/users/register", json=REGISTER_PAYLOAD)
    response = await client.post("/api/users/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 400
    assert response.json()["success"] is False


@pytest.mark.asyncio
async def test_register_user_accepts_sms_preferences(client: AsyncClient) -> None:
    """Registration should persist SMS preferences for the hackathon MVP."""
    payload = {
        **REGISTER_PAYLOAD,
        "sms_opt_in": True,
        "preferred_language": "Luganda",
    }
    response = await client.post("/api/users/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["sms_opt_in"] is True
    assert data["user"]["preferred_language"] == "Luganda"


@pytest.mark.asyncio
async def test_get_user(client: AsyncClient) -> None:
    """GET /api/users/{phone_number} should return the registered user."""
    await client.post("/api/users/register", json=REGISTER_PAYLOAD)
    response = await client.get(f"/api/users/{REGISTER_PAYLOAD['phone_number']}")
    assert response.status_code == 200
    assert response.json()["name"] == "Grace"


@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient) -> None:
    """GET /api/users/{phone_number} should 404 for unknown users."""
    response = await client.get("/api/users/+256799999999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_invalid_phone_number(client: AsyncClient) -> None:
    """Invalid phone numbers should be rejected."""
    payload = {**REGISTER_PAYLOAD, "phone_number": "invalid"}
    response = await client.post("/api/users/register", json=payload)
    assert response.status_code == 422
    assert response.json()["success"] is False


@pytest.mark.asyncio
async def test_invalid_life_stage(client: AsyncClient) -> None:
    """Invalid life stage values should be rejected."""
    payload = {**REGISTER_PAYLOAD, "life_stage": "InvalidStage"}
    response = await client.post("/api/users/register", json=payload)
    assert response.status_code == 422
