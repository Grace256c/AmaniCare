"""USSD Pydantic schemas."""

from pydantic import BaseModel, Field


class USSDRequest(BaseModel):
    """Africa's Talking USSD webhook payload."""

    sessionId: str = Field(..., description="Unique USSD session identifier")
    phoneNumber: str = Field(..., description="Caller phone number")
    text: str = Field(default="", description="Cumulative user input, *-separated")
    serviceCode: str = Field(default="", description="USSD service code dialed")


class USSDResponse(BaseModel):
    """Plain-text USSD response body."""

    response: str
