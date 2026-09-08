from sqlalchemy.orm import Session

from repositories.audit_log_repository import (
    AuditLogRepository
)

from repositories.jemaat_repository import (
    JemaatRepository
)

from repositories.refresh_token_repository import (
    RefreshTokenRepository
)

from repositories.user_repository import (
    UserRepository
)


class UnitOfWork:
    """
    Mengelola satu transaction database
    untuk seluruh repository.

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

        self.user = UserRepository(
            session
        )

        self.refresh_token = RefreshTokenRepository(
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