from sqlalchemy.orm import Session

from models.audit_log import AuditLog


class AuditLogRepository:
    """
    Repository untuk akses data Audit Log.

    Repository hanya menangani operasi data.
    Transaction dikelola oleh UnitOfWork.
    """

    def __init__(self, db: Session):
        self.db = db

    # =====================================================
    # ADD AUDIT LOG
    # =====================================================

    def add(
        self,
        audit_log: AuditLog
    ):
        self.db.add(audit_log)

    # =====================================================
    # GET BY ID
    # =====================================================

    def get_by_id(
        self,
        audit_log_id: int
    ):
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.id == audit_log_id)
            .first()
        )

    # =====================================================
    # GET BY USER
    # =====================================================

    def get_by_user(
        self,
        user_id: int
    ):
        return (
            self.db.query(AuditLog)
            .filter(
                AuditLog.user_id == user_id
            )
            .order_by(
                AuditLog.created_at.desc()
            )
            .all()
        )

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh(
        self,
        audit_log: AuditLog
    ):
        self.db.refresh(audit_log)