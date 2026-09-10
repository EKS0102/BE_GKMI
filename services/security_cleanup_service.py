from datetime import datetime, timedelta, UTC

from unit_of_work import UnitOfWork


# =========================================================
# KONFIGURASI
# =========================================================

LOGIN_ATTEMPT_RETENTION_DAYS = 30


# =========================================================
# SECURITY CLEANUP SERVICE
# =========================================================

class SecurityCleanupService:
    """
    Service untuk membersihkan data security
    yang sudah tidak diperlukan.

    Cleanup:
    - refresh token yang expired / revoked
    - login attempt yang sudah lama
    """

    def __init__(
        self,
        unit_of_work: UnitOfWork
    ):
        self.unit_of_work = unit_of_work

    # =====================================================
    # CLEANUP REFRESH TOKENS
    # =====================================================

    def cleanup_refresh_tokens(
        self
    ) -> int:
        """
        Menghapus refresh token yang sudah:
        - expired, atau
        - revoked.
        """

        now = datetime.now(
            UTC
        )

        try:
            deleted = (
                self.unit_of_work
                .refresh_token
                .delete_invalid_tokens(
                    now
                )
            )

            self.unit_of_work.commit()

        except Exception:
            self.unit_of_work.rollback()
            raise

        return deleted

    # =====================================================
    # CLEANUP LOGIN ATTEMPTS
    # =====================================================

    def cleanup_login_attempts(
        self
    ) -> int:
        """
        Menghapus login attempt yang lebih lama
        dari retention period.
        """

        now = datetime.now(
            UTC
        )

        before = (
            now
            - timedelta(
                days=LOGIN_ATTEMPT_RETENTION_DAYS
            )
        )

        try:
            deleted = (
                self.unit_of_work
                .login_attempt
                .delete_older_than(
                    before
                )
            )

            self.unit_of_work.commit()

        except Exception:
            self.unit_of_work.rollback()
            raise

        return deleted

    # =====================================================
    # CLEANUP ALL SECURITY DATA
    # =====================================================

    def cleanup_all(
        self
    ) -> dict:
        """
        Membersihkan semua data security.

        Saat ini setiap cleanup method mempunyai
        transaction masing-masing.
        """

        refresh_tokens_deleted = (
            self.cleanup_refresh_tokens()
        )

        login_attempts_deleted = (
            self.cleanup_login_attempts()
        )

        return {
            "refresh_tokens_deleted":
                refresh_tokens_deleted,
            "login_attempts_deleted":
                login_attempts_deleted
        }