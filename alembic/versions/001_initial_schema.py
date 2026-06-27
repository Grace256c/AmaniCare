"""Initial database schema for MamaCare AI."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create users, ussd_sessions, and reminders tables."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column(
            "life_stage",
            sa.Enum(
                "Teen",
                "Regular",
                "TryingToConceive",
                "Pregnant",
                "Postpartum",
                "Perimenopause",
                "Menopause",
                name="lifestage",
            ),
            nullable=False,
        ),
        sa.Column("language", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_phone_number"), "users", ["phone_number"], unique=True)

    op.create_table(
        "ussd_sessions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.String(length=100), nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=False),
        sa.Column(
            "flow",
            sa.Enum(
                "main",
                "register_name",
                "register_age",
                "register_life_stage",
                "ask_question",
                name="ussdflow",
            ),
            nullable=False,
        ),
        sa.Column("temp_name", sa.String(length=100), nullable=True),
        sa.Column("temp_age", sa.Integer(), nullable=True),
        sa.Column("temp_life_stage", sa.String(length=50), nullable=True),
        sa.Column("last_input", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ussd_sessions_session_id"), "ussd_sessions", ["session_id"], unique=True)

    op.create_table(
        "reminders",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=False),
        sa.Column(
            "reminder_type",
            sa.Enum(
                "period",
                "medication",
                "pregnancy_checkin",
                "menopause_wellness",
                name="remindertype",
            ),
            nullable=False,
        ),
        sa.Column("next_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reminders_phone_number"), "reminders", ["phone_number"], unique=False)


def downgrade() -> None:
    """Drop all MamaCare AI tables."""
    op.drop_index(op.f("ix_reminders_phone_number"), table_name="reminders")
    op.drop_table("reminders")
    op.drop_index(op.f("ix_ussd_sessions_session_id"), table_name="ussd_sessions")
    op.drop_table("ussd_sessions")
    op.drop_index(op.f("ix_users_phone_number"), table_name="users")
    op.drop_table("users")
