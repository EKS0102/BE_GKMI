from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base


class LoginAttempt(Base):
    """
    Menyimpan catatan percobaan login.

    Digunakan untuk:
    - brute-force protection
    - temporary login lock
    """

    __tablename__ = "login_attempts"

    # =====================================================
    # ID
    # =====================================================

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    # =====================================================
    # USERNAME
    # =====================================================

    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    # =====================================================
    # IP ADDRESS
    # =====================================================

    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
        index=True
    )

    # =====================================================
    # FAILED AT
    # =====================================================

    failed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    # =====================================================
    # CREATED AT
    # =====================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )