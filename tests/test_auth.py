from auth.refresh_token import hash_refresh_token

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

    assert response.json()["detail"] == (
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

    assert response.json()["detail"] == (
        "Username atau password salah"
    )


# =========================================================
# LOGIN - REFRESH TOKEN DISIMPAN
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
    # RESPONSE
    # =====================================================

    assert "access_token" in data
    assert "refresh_token" in data

    assert data["refresh_token"]

    assert data["token_type"] == "bearer"

    # =====================================================
    # DATABASE
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

    # Database menyimpan HASH, bukan token asli
    assert refresh_token.token_hash != (
        data["refresh_token"]
    )

    assert refresh_token.revoked_at is None

    assert refresh_token.expires_at > (
        refresh_token.created_at
    )


# =========================================================
# REFRESH TOKEN - ROTATION SUCCESS
# =========================================================

def test_refresh_token_success(
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

    old_refresh_token = login_response.json()[
        "refresh_token"
    ]

    # =====================================================
    # ROTATION
    # =====================================================

    response = client.post(
        "/auth/refresh",
        json={
            "refresh_token": old_refresh_token
        }
    )

    assert response.status_code == 200

    data = response.json()

    # =====================================================
    # RESPONSE
    # =====================================================

    assert data["access_token"]

    assert data["refresh_token"]

    assert data["refresh_token"] != (
        old_refresh_token
    )

    assert data["token_type"] == "bearer"

    new_refresh_token = data[
        "refresh_token"
    ]

    # =====================================================
    # TOKEN LAMA
    # =====================================================

    old_hash = hash_refresh_token(
        old_refresh_token
    )

    old_stored_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token_hash
            == old_hash
        )
        .first()
    )

    assert old_stored_token is not None

    assert old_stored_token.revoked_at is not None

    # =====================================================
    # TOKEN BARU
    # =====================================================

    new_hash = hash_refresh_token(
        new_refresh_token
    )

    new_stored_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token_hash
            == new_hash
        )
        .first()
    )

    assert new_stored_token is not None

    assert new_stored_token.revoked_at is None

    assert new_stored_token.user_id == (
        create_test_user.id
    )

    assert new_stored_token.expires_at > (
        new_stored_token.created_at
    )


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
    from datetime import UTC, datetime, timedelta

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
    # AMBIL TOKEN DARI DATABASE
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
    # EXPIRE TOKEN
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
    from datetime import UTC, datetime

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
    # AMBIL TOKEN
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
# OLD REFRESH TOKEN - REJECTED AFTER ROTATION
# =========================================================

def test_old_refresh_token_rejected_after_rotation(
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

    old_refresh_token = login_response.json()[
        "refresh_token"
    ]

    # =====================================================
    # ROTATION A → B
    # =====================================================

    first_refresh = client.post(
        "/auth/refresh",
        json={
            "refresh_token": old_refresh_token
        }
    )

    assert first_refresh.status_code == 200

    new_refresh_token = first_refresh.json()[
        "refresh_token"
    ]

    assert new_refresh_token != (
        old_refresh_token
    )

    # =====================================================
    # GUNAKAN TOKEN LAMA LAGI
    # =====================================================

    second_refresh = client.post(
        "/auth/refresh",
        json={
            "refresh_token": old_refresh_token
        }
    )

    assert second_refresh.status_code == 401

    assert second_refresh.json()["detail"] == (
        "Refresh token tidak valid"
    )


# =========================================================
# NEW REFRESH TOKEN - STILL VALID
# =========================================================

def test_new_refresh_token_still_valid(
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

    first_refresh_token = login_response.json()[
        "refresh_token"
    ]

    # =====================================================
    # ROTATION A → B
    # =====================================================

    first_refresh = client.post(
        "/auth/refresh",
        json={
            "refresh_token": first_refresh_token
        }
    )

    assert first_refresh.status_code == 200

    second_refresh_token = first_refresh.json()[
        "refresh_token"
    ]

    assert second_refresh_token != (
        first_refresh_token
    )

    # =====================================================
    # ROTATION B → C
    # =====================================================

    second_refresh = client.post(
        "/auth/refresh",
        json={
            "refresh_token": second_refresh_token
        }
    )

    assert second_refresh.status_code == 200

    data = second_refresh.json()

    # =====================================================
    # RESPONSE
    # =====================================================

    assert data["access_token"]

    assert data["refresh_token"]

    assert data["refresh_token"] != (
        second_refresh_token
    )

    assert data["token_type"] == "bearer"


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
    # REFRESH TOKEN SETELAH LOGOUT
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