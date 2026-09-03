"""initial migration

Revision ID: ee51ec6873a7
Revises:
Create Date: 2026-09-03 10:38:04.741065

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ee51ec6873a7"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial database schema."""

    # =====================================================
    # USERS
    # =====================================================

    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "username",
            sa.String(length=50),
            nullable=False
        ),
        sa.Column(
            "password_hash",
            sa.Text(),
            nullable=False
        ),
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "username",
            name="uq_users_username"
        )
    )

    op.create_index(
        "ix_users_id",
        "users",
        ["id"],
        unique=False
    )

    # =====================================================
    # JEMAAT
    # =====================================================

    op.create_table(
        "jemaat",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "nama_panggilan",
            sa.String(length=100),
            nullable=False
        ),
        sa.Column(
            "nama_lengkap",
            sa.String(length=150),
            nullable=False
        ),
        sa.Column(
            "jenis_kelamin",
            sa.String(length=20),
            nullable=False
        ),
        sa.Column(
            "tanggal_lahir",
            sa.Date(),
            nullable=False
        ),
        sa.Column(
            "domisili",
            sa.Text(),
            nullable=False
        ),
        sa.Column(
            "status_jemaat",
            sa.String(length=20),
            nullable=False
        ),
        sa.Column(
            "status_diakonia",
            sa.String(length=10),
            nullable=False
        ),
        sa.Column(
            "kelompok_ibadah",
            sa.String(length=30),
            nullable=False
        ),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        "ix_jemaat_id",
        "jemaat",
        ["id"],
        unique=False
    )


def downgrade() -> None:
    """Drop initial database schema."""

    op.drop_index(
        "ix_jemaat_id",
        table_name="jemaat"
    )

    op.drop_table("jemaat")

    op.drop_index(
        "ix_users_id",
        table_name="users"
    )

    op.drop_table("users")