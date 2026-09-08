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
    """
    Membuat AuthService menggunakan Mock UnitOfWork.

    UnitOfWork memiliki:
    - user repository
    - refresh_token repository
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

    unit_of_work.user.add.assert_called_once()

    unit_of_work.commit.assert_called_once()

    unit_of_work.rollback.assert_called_once()

    unit_of_work.user.refresh.assert_not_called()