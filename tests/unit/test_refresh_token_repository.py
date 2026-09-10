from datetime import UTC, datetime, timedelta

from models.refresh_token import RefreshToken
from repositories.refresh_token_repository import (
    RefreshTokenRepository
)


# =========================================================
# DELETE INVALID TOKENS
# =========================================================

def test_delete_invalid_tokens(
    db,
    create_test_user
):
    repository = RefreshTokenRepository(
        db
    )

    now = datetime.now(UTC)

    # =====================================================
    # TOKEN REVOKED
    # =====================================================

    revoked_token = RefreshToken(
        user_id=create_test_user.id,
        token_hash="revoked-token-hash",
        expires_at=now + timedelta(days=7),
        revoked_at=now,
        created_at=now
    )

    # =====================================================
    # TOKEN EXPIRED
    # =====================================================

    expired_token = RefreshToken(
        user_id=create_test_user.id,
        token_hash="expired-token-hash",
        expires_at=now - timedelta(days=1),
        revoked_at=None,
        created_at=now - timedelta(days=2)
    )

    # =====================================================
    # TOKEN AKTIF
    # =====================================================

    active_token = RefreshToken(
        user_id=create_test_user.id,
        token_hash="active-token-hash",
        expires_at=now + timedelta(days=7),
        revoked_at=None,
        created_at=now
    )

    repository.add(
        revoked_token
    )

    repository.add(
        expired_token
    )

    repository.add(
        active_token
    )

    db.commit()

    # =====================================================
    # DELETE
    # =====================================================

    deleted = repository.delete_invalid_tokens(
        now
    )

    db.commit()

    # =====================================================
    # HARUS MENGHAPUS 2 TOKEN
    # =====================================================

    assert deleted == 2

    # =====================================================
    # TOKEN AKTIF HARUS TETAP ADA
    # =====================================================

    remaining = (
        db.query(RefreshToken)
        .all()
    )

    assert len(remaining) == 1

    assert remaining[0].token_hash == (
        "active-token-hash"
    )