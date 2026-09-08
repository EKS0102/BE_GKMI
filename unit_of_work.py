from sqlalchemy.orm import Session

from repositories.audit_log_repository import (
    AuditLogRepository
)

from repositories.jemaat_repository import (
    JemaatRepository
)


class UnitOfWork:
    """
    Mengelola satu transaction database
    untuk beberapa repository.

    Semua repository menggunakan Session yang sama.
    """

    def __init__(
        self,
        session: Session
    ):
        self.session = session

        # =================================================
        # REPOSITORIES
        # =================================================

        self.jemaat = JemaatRepository(
            session
        )

        self.audit_log = AuditLogRepository(
            session
        )

    # =====================================================
    # COMMIT
    # =====================================================

    def commit(self):
        self.session.commit()

    # =====================================================
    # ROLLBACK
    # =====================================================

    def rollback(self):
        self.session.rollback()