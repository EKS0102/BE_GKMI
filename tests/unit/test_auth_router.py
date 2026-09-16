from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from routers.auth import (
    register,
    login,
    refresh_access_token,
    logout,
)


def make_integrity_error():
    return IntegrityError(
        "statement",
        {},
        Exception("database integrity error")
    )


def test_register_integrity_error():
    service = MagicMock()

    service.get_user_by_username.return_value = None
    service.get_user_by_email.return_value = None
    service.create_user.side_effect = make_integrity_error()

    data = MagicMock()
    data.username = "newuser"
    data.password = "password123"
    data.role.value = "staff"
    data.email = "newuser@test.com"

    with pytest.raises(HTTPException) as exc_info:
        register(
            data=data,
            service=service
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "Username atau email sudah digunakan"
    )


def test_login_integrity_error():
    service = MagicMock()
    service.login.side_effect = make_integrity_error()

    data = MagicMock()
    data.username = "admin"
    data.password = "admin123"

    request = MagicMock()
    request.client = None

    with pytest.raises(HTTPException) as exc_info:
        login(
            data=data,
            request=request,
            service=service
        )

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == (
        "Gagal membuat session login"
    )

    service.login.assert_called_once_with(
        username="admin",
        password="admin123",
        ip_address=None
    )


def test_refresh_access_token_integrity_error():
    service = MagicMock()
    service.refresh_access_token.side_effect = (
        make_integrity_error()
    )

    data = MagicMock()
    data.refresh_token = "test-refresh-token"

    request = MagicMock()
    request.client = None

    with pytest.raises(HTTPException) as exc_info:
        refresh_access_token(
            data=data,
            request=request,
            service=service
        )

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == (
        "Gagal memperbarui session"
    )

    service.refresh_access_token.assert_called_once_with(
        raw_refresh_token="test-refresh-token",
        ip_address=None
    )


def test_logout_integrity_error():
    service = MagicMock()
    service.revoke_refresh_token.side_effect = (
        make_integrity_error()
    )

    data = MagicMock()
    data.refresh_token = "test-refresh-token"

    with pytest.raises(HTTPException) as exc_info:
        logout(
            data=data,
            service=service
        )

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == (
        "Gagal melakukan logout"
    )

    service.revoke_refresh_token.assert_called_once_with(
        "test-refresh-token"
    )