# =========================================================
# 401 - TANPA TOKEN
# =========================================================

def test_get_jemaat_without_token(client):
    response = client.get(
        "/jemaat"
    )

    assert response.status_code == 401


# =========================================================
# 401 - TOKEN INVALID
# =========================================================

def test_get_jemaat_invalid_token(client):
    response = client.get(
        "/jemaat",
        headers={
            "Authorization": "Bearer token_salah"
        }
    )

    assert response.status_code == 401


# =========================================================
# 401 - FORMAT AUTHORIZATION SALAH
# =========================================================

def test_get_jemaat_invalid_authorization_format(client):
    response = client.get(
        "/jemaat",
        headers={
            "Authorization": "Token token_salah"
        }
    )

    assert response.status_code == 401


# =========================================================
# 401 - TOKEN KOSONG
# =========================================================

def test_get_jemaat_empty_token(client):
    response = client.get(
        "/jemaat",
        headers={
            "Authorization": "Bearer "
        }
    )

    assert response.status_code == 401


# =========================================================
# 403 - VIEWER CREATE
# =========================================================

def test_viewer_cannot_create_jemaat_security(
    client,
    viewer_token
):
    response = client.post(
        "/jemaat",
        headers={
            "Authorization": f"Bearer {viewer_token}"
        },
        json={
            "nama_panggilan": "Security",
            "nama_lengkap": "Test Security",
            "jenis_kelamin": "Laki-Laki",
            "tanggal_lahir": "2000-01-01",
            "domisili": "Salatiga",
            "status_jemaat": "Jemaat",
            "status_diakonia": "Tidak",
            "kelompok_ibadah": "Youth"
        }
    )

    assert response.status_code == 403


# =========================================================
# 403 - VIEWER UPDATE
# =========================================================

def test_viewer_cannot_update_jemaat_security(
    client,
    viewer_token
):
    response = client.put(
        "/jemaat/999999",
        headers={
            "Authorization": f"Bearer {viewer_token}"
        },
        json={
            "nama_panggilan": "Security",
            "nama_lengkap": "Test Security",
            "jenis_kelamin": "Laki-Laki",
            "tanggal_lahir": "2000-01-01",
            "domisili": "Salatiga",
            "status_jemaat": "Jemaat",
            "status_diakonia": "Tidak",
            "kelompok_ibadah": "Youth"
        }
    )

    assert response.status_code == 403


# =========================================================
# 403 - VIEWER DELETE
# =========================================================

def test_viewer_cannot_delete_jemaat_security(
    client,
    viewer_token
):
    response = client.delete(
        "/jemaat/999999",
        headers={
            "Authorization": f"Bearer {viewer_token}"
        }
    )

    assert response.status_code == 403


# =========================================================
# 403 - STAFF DELETE
# =========================================================

def test_staff_cannot_delete_jemaat_security(
    client,
    staff_token
):
    response = client.delete(
        "/jemaat/999999",
        headers={
            "Authorization": f"Bearer {staff_token}"
        }
    )

    assert response.status_code == 403


# =========================================================
# USER TIDAK AKTIF
# =========================================================

def test_inactive_user_cannot_login(
    client,
    db
):
    from models.user import User
    from pwdlib import PasswordHash

    password_hash = PasswordHash.recommended()

    user = User(
        username="inactive",
        password_hash=password_hash.hash(
            "inactive123"
        ),
        role="staff",
        is_active=False,
        email="inactive@test.com"
    )

    db.add(user)
    db.commit()

    response = client.post(
        "/auth/login",
        json={
            "username": "inactive",
            "password": "inactive123"
        }
    )

    assert response.status_code == 403

    data = response.json()

    assert data["detail"] == "User tidak aktif"


# =========================================================
# TOKEN EXPIRED
# =========================================================

def test_expired_token(client):
    import jwt
    from config import SECRET_KEY, ALGORITHM

    expired_token = jwt.encode(
        {
            "sub": "admin",
            "role": "admin",
            "exp": 0
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    response = client.get(
        "/jemaat",
        headers={
            "Authorization": f"Bearer {expired_token}"
        }
    )

    assert response.status_code == 401