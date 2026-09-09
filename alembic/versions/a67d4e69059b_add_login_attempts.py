"""add login attempts

Revision ID: a67d4e69059b
Revises: 9d58d926fe73
Create Date: 2026-09-09 15:33:29.328481

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a67d4e69059b'
down_revision: Union[str, Sequence[str], None] = '9d58d926fe73'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        'login_attempts',
        sa.Column(
            'id',
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            'username',
            sa.String(length=50),
            nullable=False
        ),
        sa.Column(
            'ip_address',
            sa.String(length=45),
            nullable=True
        ),
        sa.Column(
            'failed_at',
            sa.DateTime(),
            nullable=False
        ),
        sa.Column(
            'created_at',
            sa.DateTime(),
            nullable=False
        ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_login_attempts_failed_at'),
        'login_attempts',
        ['failed_at'],
        unique=False
    )

    op.create_index(
        op.f('ix_login_attempts_id'),
        'login_attempts',
        ['id'],
        unique=False
    )

    op.create_index(
        op.f('ix_login_attempts_ip_address'),
        'login_attempts',
        ['ip_address'],
        unique=False
    )

    op.create_index(
        op.f('ix_login_attempts_username'),
        'login_attempts',
        ['username'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f('ix_login_attempts_username'),
        table_name='login_attempts'
    )

    op.drop_index(
        op.f('ix_login_attempts_ip_address'),
        table_name='login_attempts'
    )

    op.drop_index(
        op.f('ix_login_attempts_id'),
        table_name='login_attempts'
    )

    op.drop_index(
        op.f('ix_login_attempts_failed_at'),
        table_name='login_attempts'
    )

    op.drop_table(
        'login_attempts'
    )
