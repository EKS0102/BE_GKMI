# =========================================================
# DATA TEST
# =========================================================

JEMAAT_DATA = {
    "nama_panggilan": "Budi",
    "nama_lengkap": "Budi Test",
    "jenis_kelamin": "Laki-Laki",
    "tanggal_lahir": "2000-05-15",
    "domisili": "Jl. Diponegoro No. 10, Salatiga",
    "status_jemaat": "Jemaat",
    "status_diakonia": "Ya",
    "kelompok_ibadah": "Youth"
}


JEMAAT_UPDATE_DATA = {
    "nama_panggilan": "Budi Update",
    "nama_lengkap": "Budi Test Update",
    "jenis_kelamin": "Laki-Laki",
    "tanggal_lahir": "2000-05-15",
    "domisili": "Jl. Diponegoro No. 20, Salatiga",
    "status_jemaat": "Jemaat",
    "status_diakonia": "Tidak",
    "kelompok_ibadah": "Kompak"
}


# =========================================================
# HELPER
# =========================================================

def create_jemaat(
    client,
    token,
    data=None
):
    if data is None:
        data = JEMAAT_DATA

    response = client.post(
        "/jemaat",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=data
    )

    return response


# =========================================================
# CREATE
# =========================================================

def test_create_jemaat(
    client,
    admin_token
):
    response = create_jemaat(
        client,
        admin_token
    )

    assert response.status_code == 201

    data = response.json()

    assert data["message"] == (
        "Jemaat berhasil ditambahkan"
    )

    assert "data" in data

    jemaat = data["data"]

    assert "id" in jemaat
    assert jemaat["nama_panggilan"] == "Budi"
    assert jemaat["nama_lengkap"] == "Budi Test"
    assert jemaat["jenis_kelamin"] == "Laki-Laki"
    assert jemaat["status_jemaat"] == "Jemaat"
    assert jemaat["status_diakonia"] == "Ya"
    assert jemaat["kelompok_ibadah"] == "Youth"


# =========================================================
# GET BY ID
# =========================================================

def test_get_jemaat_by_id(
    client,
    admin_token
):
    create_response = create_jemaat(
        client,
        admin_token
    )

    assert create_response.status_code == 201

    jemaat_id = (
        create_response
        .json()["data"]["id"]
    )

    response = client.get(
        f"/jemaat/{jemaat_id}",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == jemaat_id
    assert data["nama_lengkap"] == "Budi Test"


# =========================================================
# GET BY ID - NOT FOUND
# =========================================================

def test_get_jemaat_not_found(
    client,
    admin_token
):
    response = client.get(
        "/jemaat/999999",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == (
        "Jemaat tidak ditemukan"
    )


# =========================================================
# UPDATE
# =========================================================

def test_update_jemaat(
    client,
    admin_token
):
    create_response = create_jemaat(
        client,
        admin_token
    )

    assert create_response.status_code == 201

    jemaat_id = (
        create_response
        .json()["data"]["id"]
    )

    response = client.put(
        f"/jemaat/{jemaat_id}",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json=JEMAAT_UPDATE_DATA
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == (
        "Jemaat berhasil diperbarui"
    )

    jemaat = data["data"]

    assert jemaat["id"] == jemaat_id
    assert jemaat["nama_panggilan"] == (
        "Budi Update"
    )
    assert jemaat["nama_lengkap"] == (
        "Budi Test Update"
    )
    assert jemaat["domisili"] == (
        "Jl. Diponegoro No. 20, Salatiga"
    )
    assert jemaat["status_diakonia"] == "Tidak"
    assert jemaat["kelompok_ibadah"] == "Kompak"


# =========================================================
# UPDATE - NOT FOUND
# =========================================================

def test_update_jemaat_not_found(
    client,
    admin_token
):
    response = client.put(
        "/jemaat/999999",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json=JEMAAT_UPDATE_DATA
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == (
        "Jemaat tidak ditemukan"
    )


# =========================================================
# DELETE
# =========================================================

def test_delete_jemaat(
    client,
    admin_token
):
    create_response = create_jemaat(
        client,
        admin_token
    )

    assert create_response.status_code == 201

    jemaat_id = (
        create_response
        .json()["data"]["id"]
    )

    response = client.delete(
        f"/jemaat/{jemaat_id}",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 204

    # Pastikan benar-benar sudah tidak ada
    get_response = client.get(
        f"/jemaat/{jemaat_id}",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert get_response.status_code == 404


# =========================================================
# DELETE - NOT FOUND
# =========================================================

def test_delete_jemaat_not_found(
    client,
    admin_token
):
    response = client.delete(
        "/jemaat/999999",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == (
        "Jemaat tidak ditemukan"
    )


# =========================================================
# VALIDATION
# =========================================================

def test_create_jemaat_invalid_gender(
    client,
    admin_token
):
    data = JEMAAT_DATA.copy()

    data["jenis_kelamin"] = "Tidak Valid"

    response = create_jemaat(
        client,
        admin_token,
        data
    )

    assert response.status_code == 422


def test_create_jemaat_invalid_status(
    client,
    admin_token
):
    data = JEMAAT_DATA.copy()

    data["status_jemaat"] = "Tidak Valid"

    response = create_jemaat(
        client,
        admin_token,
        data
    )

    assert response.status_code == 422