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

from repositories.login_attempt_repository import (
    LoginAttemptRepository
)


class UnitOfWork:
    """
    Mengelola satu transaction database
    untuk beberapa repository.

    Semua repository menggunakan Session yang sama.

    Mendukung context manager:

        with UnitOfWork(session) as uow:
            ...
    """

    def __init__(
        self,
        session: Session
    ):
        self.session = session

        # =================================================
        # REPOSITORIES
        # =================================================

        self.user = UserRepository(
            session
        )

        self.jemaat = JemaatRepository(
            session
        )

        self.audit_log = AuditLogRepository(
            session
        )

        self.refresh_token = RefreshTokenRepository(
            session
        )

        self.login_attempt = LoginAttemptRepository(
            session
        )

    # =====================================================
    # CONTEXT MANAGER - ENTER
    # =====================================================

    def __enter__(
        self
    ):
        return self

    # =====================================================
    # CONTEXT MANAGER - EXIT
    # =====================================================

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback
    ):
        if exc_type is not None:
            self.rollback()
            return False

        self.commit()

        return False

    # =====================================================
    # COMMIT
    # =====================================================

    def commit(
        self
    ):
        self.session.commit()

    # =====================================================
    # ROLLBACK
    # =====================================================

    def rollback(
        self
    ):
        self.session.rollback()