from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

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

# =========================================================
# REFRESH TOKEN
# =========================================================

def test_refresh():

    db = MagicMock()

    repository = RefreshTokenRepository(db)

    refresh_token = MagicMock()

    repository.refresh(refresh_token)

    db.refresh.assert_called_once_with(
        refresh_token
    )

# =========================================================
# GET ACTIVE TOKEN - FOR UPDATE
# =========================================================

def test_get_active_by_token_hash_for_update():

    db = MagicMock()
    repository = RefreshTokenRepository(db)

    mock_query = MagicMock()
    mock_locked_query = MagicMock()
    mock_token = MagicMock()

    db.query.return_value = mock_query

    # filter() tetap mengembalikan query yang sama
    mock_query.filter.return_value = mock_query

    # with_for_update() mengembalikan query berikutnya
    mock_query.with_for_update.return_value = mock_locked_query

    # first() pada query yang sudah di-lock mengembalikan token
    mock_locked_query.first.return_value = mock_token

    result = repository.get_active_by_token_hash(
        token_hash="test-token-hash",
        now=datetime.now(),
        for_update=True
    )

    assert result is mock_token

    assert mock_query.with_for_update.called
    mock_query.with_for_update.assert_called_once_with()

    mock_locked_query.first.assert_called_once_with()

# =========================================================
# GET ACTIVE TOKENS BY USER
# =========================================================

def test_get_active_by_user():

    db = MagicMock()
    repository = RefreshTokenRepository(db)

    mock_query = MagicMock()
    mock_result = [
        MagicMock(),
        MagicMock(),
    ]

    db.query.return_value = mock_query

    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.all.return_value = mock_result

    result = repository.get_active_by_user(
        user_id=1,
        now=datetime.now()
    )

    assert result == mock_result

    db.query.assert_called_once_with(
        RefreshToken
    )

    mock_query.filter.assert_called_once()
    mock_query.order_by.assert_called_once()
    mock_query.all.assert_called_once_with()
