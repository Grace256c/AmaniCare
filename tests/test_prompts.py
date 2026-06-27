"""Prompt builder unit tests."""

from app.models.user import LifeStage, User
from app.utils.prompts import build_prompt


def test_build_prompt_includes_user_profile() -> None:
    """Prompt should include age, life stage, language, and question."""
    user = User(
        id=1,
        phone_number="+256700000000",
        name="Grace",
        age=23,
        life_stage=LifeStage.REGULAR,
        language="English",
    )
    question = "I have severe period cramps."

    prompt = build_prompt(user, question)

    assert "MamaCare AI" in prompt
    assert "Age: 23" in prompt
    assert "Life stage: Regular" in prompt
    assert "Language: English" in prompt
    assert question in prompt
    assert "Never diagnose" in prompt
