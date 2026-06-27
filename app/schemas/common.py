"""Common API response schemas."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"


class ErrorResponse(BaseModel):
    """Standard error response envelope."""

    success: bool = False
    message: str
