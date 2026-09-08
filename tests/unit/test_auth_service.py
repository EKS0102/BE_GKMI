from unittest.mock import Mock

from sqlalchemy.exc import IntegrityError

from models.user import User
from services.auth_service import AuthService


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

    repository = Mock()

    service = AuthService(
        repository
    )

    return service, repository


# =========================================================
# GET USER BY USERNAME - FOUND
# =========================================================

def test_get_user_by_username_found():

    service, repository = create_service()

    expected = create_user_model()

    repository.get_by_username.return_value = (
        expected
    )

    result = service.get_user_by_username(
        "admin"
    )

    assert result == expected

    repository.get_by_username.assert_called_once_with(
        "admin"
    )


# =========================================================
# GET USER BY USERNAME - NOT FOUND
# =========================================================

def test_get_user_by_username_not_found():

    service, repository = create_service()

    repository.get_by_username.return_value = None

    result = service.get_user_by_username(
        "tidakada"
    )

    assert result is None

    repository.get_by_username.assert_called_once_with(
        "tidakada"
    )


# =========================================================
# GET USER BY EMAIL - FOUND
# =========================================================

def test_get_user_by_email_found():

    service, repository = create_service()

    expected = create_user_model()

    repository.get_by_email.return_value = (
        expected
    )

    result = service.get_user_by_email(
        "admin@test.com"
    )

    assert result == expected

    repository.get_by_email.assert_called_once_with(
        "admin@test.com"
    )


# =========================================================
# GET USER BY EMAIL - NOT FOUND
# =========================================================

def test_get_user_by_email_not_found():

    service, repository = create_service()

    repository.get_by_email.return_value = None

    result = service.get_user_by_email(
        "tidakada@test.com"
    )

    assert result is None

    repository.get_by_email.assert_called_once_with(
        "tidakada@test.com"
    )


# =========================================================
# CREATE USER
# =========================================================

def test_create_user():

    service, repository = create_service()

    result = service.create_user(
        username="admin",
        password_hash="hashed-password",
        role="admin",
        email="admin@test.com"
    )

    assert result is not None

    assert result.username == "admin"
    assert result.password_hash == "hashed-password"
    assert result.role == "admin"
    assert result.is_active is True
    assert result.email == "admin@test.com"

    repository.add.assert_called_once()

    repository.commit.assert_called_once()

    repository.refresh.assert_called_once_with(
        result
    )


# =========================================================
# CREATE USER - INTEGRITY ERROR
# =========================================================

def test_create_user_integrity_error():

    service, repository = create_service()

    repository.commit.side_effect = IntegrityError(
        "INSERT",
        {},
        Exception("duplicate key")
    )

    try:

        service.create_user(
            username="admin",
            password_hash="hashed-password",
            role="admin",
            email="admin@test.com"
        )

        assert False, (
            "IntegrityError seharusnya dilempar"
        )

    except IntegrityError:

        pass

    repository.add.assert_called_once()

    repository.commit.assert_called_once()

    repository.rollback.assert_called_once()