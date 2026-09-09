from datetime import UTC, datetime, timedelta

from models.refresh_token import RefreshToken


# =========================================================
# LOGIN - SUCCESS
# =========================================================

def test_login_success(
    client,
    create_test_user
):
    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["access_token"]

    assert "refresh_token" in data
    assert data["refresh_token"]

    assert data["token_type"] == "bearer"


# =========================================================
# LOGIN - WRONG PASSWORD
# =========================================================

def test_login_wrong_password(
    client,
    create_test_user
):
    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "password-salah"
        }
    )

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == (
        "Username atau password salah"
    )


# =========================================================
# LOGIN - UNKNOWN USER
# =========================================================

def test_login_unknown_user(
    client
):
    response = client.post(
        "/auth/login",
        json={
            "username": "tidakada",
            "password": "admin123"
        }
    )

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == (
        "Username atau password salah"
    )


# =========================================================
# LOGIN - REFRESH TOKEN
# =========================================================

def test_login_returns_refresh_token(
    client,
    create_test_user,
    db
):
    response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    # =====================================================
    # CEK RESPONSE
    # =====================================================

    assert "access_token" in data
    assert "refresh_token" in data

    assert data["refresh_token"]

    assert data["token_type"] == "bearer"

    # =====================================================
    # CEK DATABASE
    # =====================================================

    refresh_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.user_id
            == create_test_user.id
        )
        .first()
    )

    assert refresh_token is not None

    # Database tidak boleh menyimpan token asli
    assert refresh_token.token_hash != (
        data["refresh_token"]
    )

    assert refresh_token.revoked_at is None

    assert refresh_token.expires_at > (
        refresh_token.created_at
    )


# =========================================================
# REFRESH TOKEN - SUCCESS
# =========================================================

def test_refresh_token_success(
    client,
    create_test_user
):
    # =====================================================
    # LOGIN
    # =====================================================

    login_response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    refresh_token = login_response.json()[
        "refresh_token"
    ]

    # =====================================================
    # REFRESH
    # =====================================================

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token
        }
    )

    assert response.status_code == 200

    data = response.json()

    # =====================================================
    # RESPONSE
    # =====================================================

    assert "access_token" in data
    assert data["access_token"]

    assert data["token_type"] == "bearer"

    # Versi sekarang belum menggunakan rotation
    assert "refresh_token" not in data


# =========================================================
# REFRESH TOKEN - INVALID
# =========================================================

def test_refresh_token_invalid(
    client
):
    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": "invalid-refresh-token"
        }
    )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Refresh token tidak valid"
    )


# =========================================================
# REFRESH TOKEN - EMPTY
# =========================================================

def test_refresh_token_empty(
    client
):
    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": ""
        }
    )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Refresh token tidak valid"
    )


# =========================================================
# REFRESH TOKEN - EXPIRED
# =========================================================

def test_refresh_token_expired(
    client,
    create_test_user,
    db
):
    # =====================================================
    # LOGIN
    # =====================================================

    login_response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    refresh_token = login_response.json()[
        "refresh_token"
    ]

    # =====================================================
    # CARI TOKEN
    # =====================================================

    stored_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.user_id
            == create_test_user.id
        )
        .first()
    )

    assert stored_token is not None

    # =====================================================
    # BUAT TOKEN EXPIRED
    # =====================================================

    stored_token.expires_at = (
        datetime.now(UTC)
        - timedelta(days=1)
    )

    db.commit()

    # =====================================================
    # REFRESH
    # =====================================================

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token
        }
    )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Refresh token tidak valid"
    )


# =========================================================
# REFRESH TOKEN - REVOKED
# =========================================================

def test_refresh_token_revoked(
    client,
    create_test_user,
    db
):
    # =====================================================
    # LOGIN
    # =====================================================

    login_response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    refresh_token = login_response.json()[
        "refresh_token"
    ]

    # =====================================================
    # CARI TOKEN
    # =====================================================

    stored_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.user_id
            == create_test_user.id
        )
        .first()
    )

    assert stored_token is not None

    # =====================================================
    # REVOKE TOKEN
    # =====================================================

    stored_token.revoked_at = datetime.now(
        UTC
    )

    db.commit()

    # =====================================================
    # REFRESH
    # =====================================================

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token
        }
    )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Refresh token tidak valid"
    )
    
# =========================================================
# LOGOUT - SUCCESS
# =========================================================

def test_logout_success(
    client,
    create_test_user,
    db
):
    # =====================================================
    # LOGIN
    # =====================================================

    login_response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    refresh_token = login_response.json()[
        "refresh_token"
    ]

    # =====================================================
    # LOGOUT
    # =====================================================

    logout_response = client.post(
        "/auth/logout",
        json={
            "refresh_token": refresh_token
        }
    )

    assert logout_response.status_code == 200

    assert logout_response.json() == {
        "message": "Logout berhasil"
    }

    # =====================================================
    # CEK DATABASE
    # =====================================================

    stored_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.user_id
            == create_test_user.id
        )
        .first()
    )

    assert stored_token is not None
    assert stored_token.revoked_at is not None


# =========================================================
# LOGOUT - INVALID TOKEN
# =========================================================

def test_logout_invalid_token(
    client
):
    response = client.post(
        "/auth/logout",
        json={
            "refresh_token": "invalid-refresh-token"
        }
    )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Refresh token tidak valid"
    )


# =========================================================
# LOGOUT THEN REFRESH
# =========================================================

def test_logout_then_refresh(
    client,
    create_test_user
):
    # =====================================================
    # LOGIN
    # =====================================================

    login_response = client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )

    assert login_response.status_code == 200

    refresh_token = login_response.json()[
        "refresh_token"
    ]

    # =====================================================
    # LOGOUT
    # =====================================================

    logout_response = client.post(
        "/auth/logout",
        json={
            "refresh_token": refresh_token
        }
    )

    assert logout_response.status_code == 200

    # =====================================================
    # REFRESH SETELAH LOGOUT
    # =====================================================

    refresh_response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token
        }
    )

    assert refresh_response.status_code == 401

    assert refresh_response.json()["detail"] == (
        "Refresh token tidak valid"
    )