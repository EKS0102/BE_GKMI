from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database.database import Base


class AuditLog(Base):
    """
    Menyimpan riwayat aktivitas user pada sistem.
    """

    __tablename__ = "audit_logs"

    # =====================================================
    # PRIMARY KEY
    # =====================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =====================================================
    # USER YANG MELAKUKAN AKSI
    # =====================================================

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # =====================================================
    # ACTION
    # Contoh: CREATE, UPDATE, DELETE, LOGIN
    # =====================================================

    action = Column(
        String(20),
        nullable=False
    )

    # =====================================================
    # RESOURCE
    # Contoh: jemaat, users
    # =====================================================

    resource = Column(
        String(50),
        nullable=False
    )

    # =====================================================
    # ID DATA YANG TERKENA AKSI
    # =====================================================

    resource_id = Column(
        Integer,
        nullable=True
    )

    # =====================================================
    # DESKRIPSI
    # =====================================================

    description = Column(
        Text,
        nullable=True
    )

    # =====================================================
    # IP ADDRESS
    # =====================================================

    ip_address = Column(
        String(45),
        nullable=True
    )

    # =====================================================
    # WAKTU AKSI
    # =====================================================

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # =====================================================
    # RELATIONSHIP KE USER
    # =====================================================

    user = relationship(
        "User",
        backref="audit_logs"
    )