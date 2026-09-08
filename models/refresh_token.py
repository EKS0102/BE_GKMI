from datetime import datetime, UTC

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text
)
from sqlalchemy.orm import relationship

from database.database import Base


class RefreshToken(Base):
    """
    Menyimpan refresh token yang aktif maupun yang
    sudah dicabut.
    """

    __tablename__ = "refresh_tokens"

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =====================================================
    # USER PEMILIK REFRESH TOKEN
    # =====================================================

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # =====================================================
    # HASH REFRESH TOKEN
    # =====================================================

    token_hash = Column(
        Text,
        unique=True,
        nullable=False,
        index=True
    )

    # =====================================================
    # EXPIRED TIME
    # =====================================================

    expires_at = Column(
        DateTime,
        nullable=False
    )

    # =====================================================
    # REVOKED TIME
    #
    # NULL     = masih aktif
    # NOT NULL = sudah dicabut
    # =====================================================

    revoked_at = Column(
        DateTime,
        nullable=True
    )

    # =====================================================
    # CREATED TIME
    # =====================================================

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False
    )

    # =====================================================
    # IP ADDRESS
    # =====================================================

    ip_address = Column(
        String(45),
        nullable=True
    )

    # =====================================================
    # RELATIONSHIP KE USER
    # =====================================================

    user = relationship(
        "User",
        backref="refresh_tokens"
    )