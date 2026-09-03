def test_register_success(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "andi",
            "password": "andi123",
            "role": "staff",
            "email": "andi@test.com"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "andi"
    assert data["role"] == "staff"
    assert data["is_active"] is True
    assert data["email"] == "andi@test.com"

    # Password tidak boleh muncul
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_username(
    client,
    create_test_user
):
    response = client.post(
        "/auth/register",
        json={
            "username": "admin",
            "password": "password123",
            "role": "staff",
            "email": "admin2@test.com"
        }
    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"] == "Username sudah digunakan"


def test_register_duplicate_email(
    client,
    create_test_user
):
    response = client.post(
        "/auth/register",
        json={
            "username": "admin2",
            "password": "password123",
            "role": "staff",
            "email": "admin@test.com"
        }
    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"] == "Email sudah digunakan"


def test_register_invalid_email(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "andi2",
            "password": "andi123",
            "role": "staff",
            "email": "bukan-email"
        }
    )

    assert response.status_code == 422