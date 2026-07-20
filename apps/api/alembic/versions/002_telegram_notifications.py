"""telegram notifications

Revision ID: 002
Revises: 001
Create Date: 2026-07-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "customers",
        sa.Column("notify_channel", sa.String(), nullable=False, server_default="email"),
    )
    op.add_column("customers", sa.Column("telegram_bot_token", sa.String(), nullable=True))
    op.add_column("customers", sa.Column("telegram_chat_id", sa.String(), nullable=True))
    op.add_column(
        "customers",
        sa.Column(
            "telegram_api_url",
            sa.String(),
            nullable=False,
            server_default="https://api.telegram.org",
        ),
    )


def downgrade() -> None:
    op.drop_column("customers", "telegram_api_url")
    op.drop_column("customers", "telegram_chat_id")
    op.drop_column("customers", "telegram_bot_token")
    op.drop_column("customers", "notify_channel")
