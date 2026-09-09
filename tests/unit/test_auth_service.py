from datetime import UTC, datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from models.user import User
from models.refresh_token import RefreshToken
from services.auth_service import (
    AuthService,
    REFRESH_TOKEN_EXPIRE_DAYS
)


# =========================================================
# TEST DATA
# =========================================================

def create_user_model():
    return User(
        id=1,
        username="admin",
        password_hash="hashed-password",
        role="admin",
        is_active=True,
        email="admin@test.com"
    )


# =========================================================
# HELPER
# =========================================================

def create_service():
    """
    Membuat AuthService menggunakan Mock UnitOfWork.
    """

    unit_of_work = Mock()

    unit_of_work.user = Mock()
    unit_of_work.refresh_token = Mock()

    service = AuthService(
        unit_of_work
    )

    return service, unit_of_work


# =========================================================
# GET USER BY USERNAME - FOUND
# =========================================================

def test_get_user_by_username_found():

    service, unit_of_work = create_service()

    expected = create_user_model()

    unit_of_work.user.get_by_username.return_value = (
        expected
    )

    result = service.get_user_by_username(
        "admin"
    )

    assert result == expected

    unit_of_work.user.get_by_username.assert_called_once_with(
        "admin"
    )

    unit_of_work.commit.assert_not_called()

    unit_of_work.rollback.assert_not_called()


# =========================================================
# GET USER BY USERNAME - NOT FOUND
# =========================================================

def test_get_user_by_username_not_found():

    service, unit_of_work = create_service()

    unit_of_work.user.get_by_username.return_value = None

    result = service.get_user_by_username(
        "tidakada"
    )

    assert result is None

    unit_of_work.user.get_by_username.assert_called_once_with(
        "tidakada"
    )


# =========================================================
# GET USER BY EMAIL - FOUND
# =========================================================

def test_get_user_by_email_found():

    service, unit_of_work = create_service()

    expected = create_user_model()

    unit_of_work.user.get_by_email.return_value = (
        expected
    )

    result = service.get_user_by_email(
        "admin@test.com"
    )

    assert result == expected

    unit_of_work.user.get_by_email.assert_called_once_with(
        "admin@test.com"
    )


# =========================================================
# GET USER BY EMAIL - NOT FOUND
# =========================================================

def test_get_user_by_email_not_found():

    service, unit_of_work = create_service()

    unit_of_work.user.get_by_email.return_value = None

    result = service.get_user_by_email(
        "tidakada@test.com"
    )

    assert result is None

    unit_of_work.user.get_by_email.assert_called_once_with(
        "tidakada@test.com"
    )


# =========================================================
# CREATE USER
# =========================================================

def test_create_user():

    service, unit_of_work = create_service()

    result = service.create_user(
        username="admin",
        password_hash="hashed-password",
        role="admin",
        email="admin@test.com"
    )

    assert result is not None

    assert result.username == "admin"

    assert result.password_hash == (
        "hashed-password"
    )

    assert result.role == "admin"

    assert result.is_active is True

    assert result.email == "admin@test.com"

    unit_of_work.user.add.assert_called_once()

    unit_of_work.commit.assert_called_once()

    unit_of_work.user.refresh.assert_called_once_with(
        result
    )

    unit_of_work.rollback.assert_not_called()


# =========================================================
# CREATE USER - INTEGRITY ERROR
# =========================================================

def test_create_user_integrity_error():

    service, unit_of_work = create_service()

    unit_of_work.commit.side_effect = IntegrityError(
        "INSERT",
        {},
        Exception("duplicate key")
    )

    with pytest.raises(IntegrityError):

        service.create_user(
            username="admin",
            password_hash="hashed-password",
            role="admin",
            email="admin@test.com"
        )

    unit_of_work.user.add.assert_called_once()

    unit_of_work.commit.assert_called_once()

    unit_of_work.rollback.assert_called_once()

    unit_of_work.user.refresh.assert_not_called()


# =========================================================
# CREATE REFRESH TOKEN
# =========================================================

@patch(
    "services.auth_service.generate_refresh_token"
)
@patch(
    "services.auth_service.hash_refresh_token"
)
def test_create_refresh_token(
    mock_hash_refresh_token,
    mock_generate_refresh_token
):

    service, unit_of_work = create_service()

    mock_generate_refresh_token.return_value = (
        "raw-refresh-token"
    )

    mock_hash_refresh_token.return_value = (
        "hashed-refresh-token"
    )

    before = datetime.now(UTC)

    result = service.create_refresh_token(
        user_id=1,
        ip_address="127.0.0.1"
    )

    after = datetime.now(UTC)

    # =====================================================
    # TOKEN ASLI DIKEMBALIKAN
    # =====================================================

    assert result == "raw-refresh-token"

    # =====================================================
    # GENERATE TOKEN
    # =====================================================

    mock_generate_refresh_token.assert_called_once()

    # =====================================================
    # HASH TOKEN
    # =====================================================

    mock_hash_refresh_token.assert_called_once_with(
        "raw-refresh-token"
    )

    # =====================================================
    # REPOSITORY ADD
    # =====================================================

    unit_of_work.refresh_token.add.assert_called_once()

    refresh_token = (
        unit_of_work
        .refresh_token
        .add
        .call_args
        .args[0]
    )

    assert isinstance(
        refresh_token,
        RefreshToken
    )

    assert refresh_token.user_id == 1

    assert refresh_token.token_hash == (
        "hashed-refresh-token"
    )

    assert refresh_token.revoked_at is None

    assert refresh_token.ip_address == (
        "127.0.0.1"
    )

    # =====================================================
    # CREATED AT
    # =====================================================

    assert before <= refresh_token.created_at <= after

    # =====================================================
    # EXPIRES AT
    # =====================================================

    expected_expiry_min = (
        before
        + timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )
    )

    expected_expiry_max = (
        after
        + timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )
    )

    assert (
        expected_expiry_min
        <= refresh_token.expires_at
        <= expected_expiry_max
    )

    # =====================================================
    # COMMIT
    # =====================================================

    unit_of_work.commit.assert_called_once()

    unit_of_work.rollback.assert_not_called()


# =========================================================
# CREATE REFRESH TOKEN - INTEGRITY ERROR
# =========================================================

@patch(
    "services.auth_service.generate_refresh_token"
)
@patch(
    "services.auth_service.hash_refresh_token"
)
def test_create_refresh_token_integrity_error(
    mock_hash_refresh_token,
    mock_generate_refresh_token
):

    service, unit_of_work = create_service()

    mock_generate_refresh_token.return_value = (
        "raw-refresh-token"
    )

    mock_hash_refresh_token.return_value = (
        "hashed-refresh-token"
    )

    unit_of_work.commit.side_effect = IntegrityError(
        "INSERT",
        {},
        Exception("duplicate key")
    )

    with pytest.raises(IntegrityError):

        service.create_refresh_token(
            user_id=1,
            ip_address="127.0.0.1"
        )

    unit_of_work.refresh_token.add.assert_called_once()

    unit_of_work.commit.assert_called_once()

    unit_of_work.rollback.assert_called_once()
    
    
    # =========================================================
# LOGIN - SUCCESS
# =========================================================

@patch(
    "services.auth_service.create_access_token"
)
@patch(
    "services.auth_service.generate_refresh_token"
)
@patch(
    "services.auth_service.hash_refresh_token"
)
def test_login_success(
    mock_hash_refresh_token,
    mock_generate_refresh_token,
    mock_create_access_token
):
    service, unit_of_work = create_service()

    user = create_user_model()

    unit_of_work.user.get_by_username.return_value = user

    mock_create_access_token.return_value = (
        "access-token"
    )

    mock_generate_refresh_token.return_value = (
        "refresh-token"
    )

    mock_hash_refresh_token.return_value = (
        "refresh-token-hash"
    )

    # PasswordHash akan benar-benar memverifikasi password,
    # jadi kita ganti menjadi Mock agar unit test fokus
    # pada business logic AuthService.
    service.password_hash = Mock()

    service.password_hash.verify.return_value = True

    result = service.login(
        username="admin",
        password="admin123",
        ip_address="127.0.0.1"
    )

    assert result is not None

    assert result["access_token"] == (
        "access-token"
    )

    assert result["refresh_token"] == (
        "refresh-token"
    )

    assert result["token_type"] == "bearer"

    unit_of_work.user.get_by_username.assert_called_once_with(
        "admin"
    )

    service.password_hash.verify.assert_called_once_with(
        "admin123",
        user.password_hash
    )

    mock_create_access_token.assert_called_once_with(
        {
            "sub": "admin",
            "role": "admin"
        }
    )

    unit_of_work.refresh_token.add.assert_called_once()

    unit_of_work.commit.assert_called_once()

    unit_of_work.rollback.assert_not_called()


# =========================================================
# LOGIN - USER NOT FOUND
# =========================================================

def test_login_user_not_found():

    service, unit_of_work = create_service()

    unit_of_work.user.get_by_username.return_value = None

    result = service.login(
        username="tidakada",
        password="password"
    )

    assert result is None

    unit_of_work.user.get_by_username.assert_called_once_with(
        "tidakada"
    )

    unit_of_work.refresh_token.add.assert_not_called()

    unit_of_work.commit.assert_not_called()


# =========================================================
# LOGIN - USER INACTIVE
# =========================================================

def test_login_user_inactive():

    service, unit_of_work = create_service()

    user = create_user_model()

    user.is_active = False

    unit_of_work.user.get_by_username.return_value = user

    result = service.login(
        username="admin",
        password="admin123"
    )

    assert result == "inactive"

    unit_of_work.refresh_token.add.assert_not_called()

    unit_of_work.commit.assert_not_called()


# =========================================================
# LOGIN - WRONG PASSWORD
# =========================================================

def test_login_wrong_password():

    service, unit_of_work = create_service()

    user = create_user_model()

    unit_of_work.user.get_by_username.return_value = user

    service.password_hash = Mock()

    service.password_hash.verify.return_value = False

    result = service.login(
        username="admin",
        password="wrong-password"
    )

    assert result is None

    service.password_hash.verify.assert_called_once_with(
        "wrong-password",
        user.password_hash
    )

    unit_of_work.refresh_token.add.assert_not_called()

    unit_of_work.commit.assert_not_called()


# =========================================================
# LOGIN - COMMIT ERROR
# =========================================================

@patch(
    "services.auth_service.create_access_token"
)
@patch(
    "services.auth_service.generate_refresh_token"
)
@patch(
    "services.auth_service.hash_refresh_token"
)
def test_login_commit_error(
    mock_hash_refresh_token,
    mock_generate_refresh_token,
    mock_create_access_token
):
    service, unit_of_work = create_service()

    user = create_user_model()

    unit_of_work.user.get_by_username.return_value = user

    service.password_hash = Mock()

    service.password_hash.verify.return_value = True

    mock_create_access_token.return_value = (
        "access-token"
    )

    mock_generate_refresh_token.return_value = (
        "refresh-token"
    )

    mock_hash_refresh_token.return_value = (
        "refresh-token-hash"
    )

    unit_of_work.commit.side_effect = IntegrityError(
        "INSERT",
        {},
        Exception("database error")
    )

    with pytest.raises(IntegrityError):

        service.login(
            username="admin",
            password="admin123"
        )

    unit_of_work.refresh_token.add.assert_called_once()

    unit_of_work.commit.assert_called_once()

    unit_of_work.rollback.assert_called_once()
    
    
# =========================================================
# REFRESH ACCESS TOKEN - ROTATION SUCCESS
# =========================================================

@patch(
    "services.auth_service.generate_refresh_token"
)
@patch(
    "services.auth_service.create_access_token"
)
@patch(
    "services.auth_service.hash_refresh_token"
)
def test_refresh_access_token_success(
    mock_hash_refresh_token,
    mock_create_access_token,
    mock_generate_refresh_token
):
    service, unit_of_work = create_service()

    # =====================================================
    # USER
    # =====================================================

    user = create_user_model()

    unit_of_work.user.get_by_id.return_value = (
        user
    )

    # =====================================================
    # OLD REFRESH TOKEN
    # =====================================================

    old_refresh_token = Mock()

    old_refresh_token.user_id = 1
    old_refresh_token.revoked_at = None

    unit_of_work.refresh_token.get_active_by_token_hash.return_value = (
        old_refresh_token
    )

    # =====================================================
    # MOCK FUNCTIONS
    # =====================================================

    mock_hash_refresh_token.side_effect = [
        "hashed-old-refresh-token",
        "hashed-new-refresh-token"
    ]

    mock_generate_refresh_token.return_value = (
        "new-refresh-token"
    )

    mock_create_access_token.return_value = (
        "new-access-token"
    )

    # =====================================================
    # EXECUTE
    # =====================================================

    result = service.refresh_access_token(
        "old-refresh-token",
        ip_address="127.0.0.1"
    )

    # =====================================================
    # RESPONSE
    # =====================================================

    assert result == {
        "access_token": "new-access-token",
        "refresh_token": "new-refresh-token",
        "token_type": "bearer"
    }

    # =====================================================
    # OLD TOKEN HASH
    # =====================================================

    assert (
        mock_hash_refresh_token.call_args_list[0].args[0]
        == "old-refresh-token"
    )

    # =====================================================
    # FIND ACTIVE TOKEN
    # =====================================================

    unit_of_work.refresh_token.get_active_by_token_hash.assert_called_once()

    # =====================================================
    # FIND USER
    # =====================================================

    unit_of_work.user.get_by_id.assert_called_once_with(
        1
    )

    # =====================================================
    # REVOKE OLD TOKEN
    # =====================================================

    unit_of_work.refresh_token.revoke.assert_called_once()

    revoke_args = (
        unit_of_work
        .refresh_token
        .revoke
        .call_args
        .args
    )

    assert revoke_args[0] is old_refresh_token

    assert isinstance(
        revoke_args[1],
        datetime
    )

    assert revoke_args[1].tzinfo == UTC

    # =====================================================
    # CREATE NEW REFRESH TOKEN
    # =====================================================

    unit_of_work.refresh_token.add.assert_called_once()

    new_refresh_token = (
        unit_of_work
        .refresh_token
        .add
        .call_args
        .args[0]
    )

    assert isinstance(
        new_refresh_token,
        RefreshToken
    )

    assert new_refresh_token.user_id == 1

    assert new_refresh_token.token_hash == (
        "hashed-new-refresh-token"
    )

    assert new_refresh_token.revoked_at is None

    assert new_refresh_token.ip_address == (
        "127.0.0.1"
    )

    # =====================================================
    # CREATE ACCESS TOKEN
    # =====================================================

    mock_create_access_token.assert_called_once_with(
        {
            "sub": "admin",
            "role": "admin"
        }
    )

    # =====================================================
    # COMMIT ONCE
    # =====================================================

    unit_of_work.commit.assert_called_once()

    unit_of_work.rollback.assert_not_called()


# =========================================================
# REFRESH ACCESS TOKEN - INVALID TOKEN
# =========================================================

@patch(
    "services.auth_service.hash_refresh_token"
)
def test_refresh_access_token_invalid_token(
    mock_hash_refresh_token
):
    service, unit_of_work = create_service()

    mock_hash_refresh_token.return_value = (
        "invalid-hash"
    )

    unit_of_work.refresh_token.get_active_by_token_hash.return_value = (
        None
    )

    result = service.refresh_access_token(
        "invalid-token"
    )

    assert result is None

    unit_of_work.user.get_by_id.assert_not_called()

    unit_of_work.commit.assert_not_called()


# =========================================================
# REFRESH ACCESS TOKEN - USER NOT FOUND
# =========================================================

@patch(
    "services.auth_service.hash_refresh_token"
)
def test_refresh_access_token_user_not_found(
    mock_hash_refresh_token
):
    service, unit_of_work = create_service()

    refresh_token = Mock()
    refresh_token.user_id = 1

    mock_hash_refresh_token.return_value = (
        "hashed-refresh-token"
    )

    unit_of_work.refresh_token.get_active_by_token_hash.return_value = (
        refresh_token
    )

    unit_of_work.user.get_by_id.return_value = None

    result = service.refresh_access_token(
        "raw-refresh-token"
    )

    assert result is None


# =========================================================
# REFRESH ACCESS TOKEN - USER INACTIVE
# =========================================================

@patch(
    "services.auth_service.hash_refresh_token"
)
def test_refresh_access_token_user_inactive(
    mock_hash_refresh_token
):
    service, unit_of_work = create_service()

    refresh_token = Mock()
    refresh_token.user_id = 1

    user = create_user_model()
    user.is_active = False

    mock_hash_refresh_token.return_value = (
        "hashed-refresh-token"
    )

    unit_of_work.refresh_token.get_active_by_token_hash.return_value = (
        refresh_token
    )

    unit_of_work.user.get_by_id.return_value = (
        user
    )

    result = service.refresh_access_token(
        "raw-refresh-token"
    )

    assert result is None

    unit_of_work.refresh_token.get_active_by_token_hash.assert_called_once()

    unit_of_work.user.get_by_id.assert_called_once_with(
        1
    )

    unit_of_work.commit.assert_not_called()

    unit_of_work.rollback.assert_not_called()


# =========================================================
# REVOKE REFRESH TOKEN - SUCCESS
# =========================================================

@patch(
    "services.auth_service.hash_refresh_token"
)
def test_revoke_refresh_token_success(
    mock_hash_refresh_token
):
    service, unit_of_work = create_service()

    refresh_token = Mock()
    refresh_token.revoked_at = None

    unit_of_work.refresh_token.get_by_token_hash.return_value = (
        refresh_token
    )

    mock_hash_refresh_token.return_value = (
        "hashed-refresh-token"
    )

    result = service.revoke_refresh_token(
        "raw-refresh-token"
    )

    assert result is True

    # =====================================================
    # HASH
    # =====================================================

    mock_hash_refresh_token.assert_called_once_with(
        "raw-refresh-token"
    )

    # =====================================================
    # FIND TOKEN
    # =====================================================

    unit_of_work.refresh_token.get_by_token_hash.assert_called_once_with(
        "hashed-refresh-token"
    )

    # =====================================================
    # REVOKE
    # =====================================================

    unit_of_work.refresh_token.revoke.assert_called_once()

    revoke_args = (
        unit_of_work
        .refresh_token
        .revoke
        .call_args
        .args
    )

    assert revoke_args[0] is refresh_token

    assert isinstance(
        revoke_args[1],
        datetime
    )

    assert revoke_args[1].tzinfo == UTC

    # =====================================================
    # COMMIT
    # =====================================================

    unit_of_work.commit.assert_called_once()

    unit_of_work.rollback.assert_not_called()


# =========================================================
# REVOKE REFRESH TOKEN - NOT FOUND
# =========================================================

@patch(
    "services.auth_service.hash_refresh_token"
)
def test_revoke_refresh_token_not_found(
    mock_hash_refresh_token
):
    service, unit_of_work = create_service()

    mock_hash_refresh_token.return_value = (
        "invalid-hash"
    )

    unit_of_work.refresh_token.get_by_token_hash.return_value = (
        None
    )

    result = service.revoke_refresh_token(
        "invalid-refresh-token"
    )

    assert result is False

    unit_of_work.refresh_token.revoke.assert_not_called()

    unit_of_work.commit.assert_not_called()

    unit_of_work.rollback.assert_not_called()


# =========================================================
# REVOKE REFRESH TOKEN - ALREADY REVOKED
# =========================================================

@patch(
    "services.auth_service.hash_refresh_token"
)
def test_revoke_refresh_token_already_revoked(
    mock_hash_refresh_token
):
    service, unit_of_work = create_service()

    refresh_token = Mock()

    refresh_token.revoked_at = datetime.now(
        UTC
    )

    unit_of_work.refresh_token.get_by_token_hash.return_value = (
        refresh_token
    )

    mock_hash_refresh_token.return_value = (
        "hashed-refresh-token"
    )

    result = service.revoke_refresh_token(
        "raw-refresh-token"
    )

    assert result is False

    unit_of_work.refresh_token.revoke.assert_not_called()

    unit_of_work.commit.assert_not_called()

    unit_of_work.rollback.assert_not_called()


# =========================================================
# REVOKE REFRESH TOKEN - COMMIT ERROR
# =========================================================

@patch(
    "services.auth_service.hash_refresh_token"
)
def test_revoke_refresh_token_commit_error(
    mock_hash_refresh_token
):
    service, unit_of_work = create_service()

    refresh_token = Mock()
    refresh_token.revoked_at = None

    unit_of_work.refresh_token.get_by_token_hash.return_value = (
        refresh_token
    )

    mock_hash_refresh_token.return_value = (
        "hashed-refresh-token"
    )

    unit_of_work.commit.side_effect = IntegrityError(
        "UPDATE",
        {},
        Exception("database error")
    )

    with pytest.raises(IntegrityError):

        service.revoke_refresh_token(
            "raw-refresh-token"
        )

    unit_of_work.refresh_token.revoke.assert_called_once()

    unit_of_work.commit.assert_called_once()

    unit_of_work.rollback.assert_called_once()