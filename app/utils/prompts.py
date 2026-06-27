"""Prompt construction utilities for Gemini health advice."""

from app.models.user import User


def build_prompt(user: User, question: str) -> str:
    """
    Build a structured prompt for Gemini using the user profile and question.

    Returns a prompt string that instructs the model to provide educational
    health guidance without diagnosing or prescribing.
    """
    return (
        "You are MamaCare AI.\n"
        "You are a women's health education assistant.\n"
        "Never diagnose.\n"
        "Never prescribe medication.\n"
        "Provide educational guidance only.\n"
        "Keep responses under 120 words.\n"
        "Always recommend seeking medical attention for emergencies.\n\n"
        "User profile\n"
        f"Age: {user.age}\n"
        f"Life stage: {user.life_stage.value}\n"
        f"Language: {user.language}\n\n"
        f"Question: {question}\n\n"
        "Return only the generated advice."
    )
