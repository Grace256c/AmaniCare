"""Security utilities for validation and future auth extensions."""

import re
import secrets

from app.core.config import get_settings

# E.164 phone format: + followed by 7-15 digits.
PHONE_PATTERN = re.compile(r"^\+[1-9]\d{6,14}$")


def validate_phone_number(phone_number: str) -> str:
    """Validate and normalize a phone number to E.164 format."""
    normalized = phone_number.strip()
    if not PHONE_PATTERN.match(normalized):
        msg = "Phone number must be in E.164 format (e.g. +256700000000)"
        raise ValueError(msg)
    return normalized


def validate_age(age: int) -> int:
    """Validate user age is within an acceptable range."""
    if age < 10 or age > 120:
        raise ValueError("Age must be between 10 and 120")
    return age


def generate_session_token() -> str:
    """Generate a secure random token for future auth flows."""
    return secrets.token_urlsafe(32)


def get_secret_key() -> str:
    """Return the application secret key."""
    return get_settings().secret_key
