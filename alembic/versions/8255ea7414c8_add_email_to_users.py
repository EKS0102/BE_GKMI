"""add email to users

Revision ID: 8255ea7414c8
Revises: ee51ec6873a7
Create Date: 2026-09-03 10:47:58.969499

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8255ea7414c8"
down_revision: Union[str, Sequence[str], None] = "ee51ec6873a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add email column to users."""

    op.add_column(
        "users",
        sa.Column(
            "email",
            sa.String(length=100),
            nullable=True
        )
    )

    op.create_unique_constraint(
        "uq_users_email",
        "users",
        ["email"]
    )


def downgrade() -> None:
    """Remove email column from users."""

    op.drop_constraint(
        "uq_users_email",
        "users",
        type_="unique"
    )

    op.drop_column(
        "users",
        "email"
    )