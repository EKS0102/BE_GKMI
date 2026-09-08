"""add refresh tokens

Revision ID: 9d58d926fe73
Revises: 277943a3753a
Create Date: 2026-09-08 15:48:24.767439

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9d58d926fe73"
down_revision: Union[str, Sequence[str], None] = "277943a3753a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "refresh_tokens",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "token_hash",
            sa.Text(),
            nullable=False
        ),

        sa.Column(
            "expires_at",
            sa.DateTime(),
            nullable=False
        ),

        sa.Column(
            "revoked_at",
            sa.DateTime(),
            nullable=True
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False
        ),

        sa.Column(
            "ip_address",
            sa.String(length=45),
            nullable=True
        ),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"]
        ),

        sa.PrimaryKeyConstraint(
            "id"
        )
    )

    op.create_index(
        op.f("ix_refresh_tokens_id"),
        "refresh_tokens",
        ["id"],
        unique=False
    )

    op.create_index(
        op.f("ix_refresh_tokens_token_hash"),
        "refresh_tokens",
        ["token_hash"],
        unique=True
    )

    op.create_index(
        op.f("ix_refresh_tokens_user_id"),
        "refresh_tokens",
        ["user_id"],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_refresh_tokens_user_id"),
        table_name="refresh_tokens"
    )

    op.drop_index(
        op.f("ix_refresh_tokens_token_hash"),
        table_name="refresh_tokens"
    )

    op.drop_index(
        op.f("ix_refresh_tokens_id"),
        table_name="refresh_tokens"
    )

    op.drop_table(
        "refresh_tokens"
    )