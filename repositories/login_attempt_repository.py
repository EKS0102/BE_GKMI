from datetime import datetime

from sqlalchemy.orm import Session

from models.login_attempt import LoginAttempt


class LoginAttemptRepository:
    """
    Repository untuk akses data percobaan login.

    Repository hanya menangani operasi database.
    Transaction commit / rollback dikelola oleh UnitOfWork.
    """

    def __init__(
        self,
        db: Session
    ):
        self.db = db

    # =====================================================
    # ADD FAILED LOGIN ATTEMPT
    # =====================================================

    def add(
        self,
        attempt: LoginAttempt
    ):
        self.db.add(attempt)

    # =====================================================
    # COUNT RECENT FAILED ATTEMPTS
    # =====================================================

    def count_recent_failed_attempts(
        self,
        username: str,
        ip_address: str | None,
        since: datetime
    ) -> int:
        query = (
            self.db.query(LoginAttempt)
            .filter(
                LoginAttempt.failed_at >= since
            )
        )

        if username:
            query = query.filter(
                LoginAttempt.username == username
            )

        if ip_address:
            query = query.filter(
                LoginAttempt.ip_address == ip_address
            )

        return query.count()

    # =====================================================
    # GET RECENT FAILED ATTEMPTS
    # =====================================================

    def get_recent_failed_attempts(
        self,
        username: str,
        ip_address: str | None,
        since: datetime
    ):
        query = (
            self.db.query(LoginAttempt)
            .filter(
                LoginAttempt.username == username,
                LoginAttempt.failed_at >= since
            )
        )

        if ip_address:
            query = query.filter(
                LoginAttempt.ip_address == ip_address
            )

        return (
            query
            .order_by(
                LoginAttempt.failed_at.desc()
            )
            .all()
        )

    # =====================================================
    # DELETE OLD ATTEMPTS
    # =====================================================

    def delete_older_than(
        self,
        before: datetime
    ) -> int:
        return (
            self.db.query(LoginAttempt)
            .filter(
                LoginAttempt.created_at < before
            )
            .delete(
                synchronize_session=False
            )
        )