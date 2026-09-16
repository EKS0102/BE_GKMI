import pytest


def test_get_current_user_invalid_payload_missing_role(monkeypatch):
    from auth.auth import get_current_user
    from fastapi import HTTPException
    from fastapi.security import HTTPAuthorizationCredentials

    monkeypatch.setattr(
        "auth.auth.jwt.decode",
        lambda *args, **kwargs: {
            "sub": "testuser"
        }
    )

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="dummy-token"
    )

    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token tidak valid"