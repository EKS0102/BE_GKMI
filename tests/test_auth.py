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
    assert data["token_type"] == "bearer"


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


def test_login_unknown_user(client):
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
    assert data["token_type"] == "bearer"

    assert data["refresh_token"]

    # =====================================================
    # CEK DATABASE
    # =====================================================

    from models.refresh_token import RefreshToken

    refresh_token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.user_id
            == create_test_user.id
        )
        .first()
    )

    assert refresh_token is not None

    assert refresh_token.token_hash != (
        data["refresh_token"]
    )

    assert refresh_token.revoked_at is None

    assert refresh_token.expires_at > (
        refresh_token.created_at
    )