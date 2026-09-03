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