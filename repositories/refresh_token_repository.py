from datetime import datetime

from sqlalchemy.orm import Session

from models.refresh_token import RefreshToken


class RefreshTokenRepository:
    """
    Repository untuk akses data Refresh Token.

    Repository hanya menangani operasi data.
    Transaction (commit / rollback) dikelola oleh UnitOfWork.
    """

    def __init__(self, db: Session):
        self.db = db

    # =====================================================
    # ADD REFRESH TOKEN
    # =====================================================

    def add(
        self,
        refresh_token: RefreshToken
    ):
        self.db.add(refresh_token)

    # =====================================================
    # GET BY TOKEN HASH
    # =====================================================

    def get_by_token_hash(
        self,
        token_hash: str
    ):
        return (
            self.db.query(RefreshToken)
            .filter(
                RefreshToken.token_hash == token_hash
            )
            .first()
        )

    # =====================================================
    # GET ACTIVE TOKEN BY HASH
    # =====================================================

    def get_active_by_token_hash(
        self,
        token_hash: str,
        now: datetime,
        for_update: bool = False
    ):
        query = (
            self.db.query(RefreshToken)
            .filter(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > now
            )
        )

        if for_update:
            query = query.with_for_update()

        return query.first()

    # =====================================================
    # GET ALL ACTIVE TOKENS BY USER
    # =====================================================

    def get_active_by_user(
        self,
        user_id: int,
        now: datetime
    ):
        return (
            self.db.query(RefreshToken)
            .filter(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > now
            )
            .order_by(
                RefreshToken.created_at.desc()
            )
            .all()
        )

    # =====================================================
    # REVOKE TOKEN
    # =====================================================

    def revoke(
        self,
        refresh_token: RefreshToken,
        revoked_at: datetime
    ):
        refresh_token.revoked_at = revoked_at

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh(
        self,
        refresh_token: RefreshToken
    ):
        self.db.refresh(
            refresh_token
        )
        
    # =====================================================
    # DELETE INVALID TOKENS
    # =====================================================

    def delete_invalid_tokens(
        self,
        now: datetime
    ) -> int:
        """
        Menghapus refresh token yang sudah tidak valid.

        Token dianggap tidak valid jika:
        - sudah di-revoke, atau
        - sudah expired.

        Transaction commit dikelola oleh UnitOfWork.
        """

        deleted = (
            self.db.query(RefreshToken)
            .filter(
                (
                    RefreshToken.revoked_at.is_not(None)
                )
                |
                (
                    RefreshToken.expires_at <= now
                )
            )
            .delete(
                synchronize_session=False
            )
        )

        return deleted