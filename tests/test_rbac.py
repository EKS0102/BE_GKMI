# =========================================================
# ADMIN
# =========================================================

def test_admin_can_get_jemaat(
    client,
    admin_token
):
    response = client.get(
        "/jemaat",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200


def test_admin_can_create_jemaat(
    client,
    admin_token
):
    response = client.post(
        "/jemaat",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "nama_panggilan": "Budi",
            "nama_lengkap": "Budi Test",
            "jenis_kelamin": "Laki-Laki",
            "tanggal_lahir": "2000-05-15",
            "domisili": "Salatiga",
            "status_jemaat": "Jemaat",
            "status_diakonia": "Ya",
            "kelompok_ibadah": "Youth"
        }
    )

    assert response.status_code == 201


def test_admin_can_update_jemaat(
    client,
    admin_token
):
    # Buat data terlebih dahulu
    create_response = client.post(
        "/jemaat",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "nama_panggilan": "Budi",
            "nama_lengkap": "Budi Test",
            "jenis_kelamin": "Laki-Laki",
            "tanggal_lahir": "2000-05-15",
            "domisili": "Salatiga",
            "status_jemaat": "Jemaat",
            "status_diakonia": "Ya",
            "kelompok_ibadah": "Youth"
        }
    )

    jemaat_id = create_response.json()["data"]["id"]

    response = client.put(
        f"/jemaat/{jemaat_id}",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "nama_panggilan": "Budi Update",
            "nama_lengkap": "Budi Test Update",
            "jenis_kelamin": "Laki-Laki",
            "tanggal_lahir": "2000-05-15",
            "domisili": "Salatiga",
            "status_jemaat": "Jemaat",
            "status_diakonia": "Tidak",
            "kelompok_ibadah": "Youth"
        }
    )

    assert response.status_code == 200


def test_admin_can_delete_jemaat(
    client,
    admin_token
):
    create_response = client.post(
        "/jemaat",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "nama_panggilan": "Budi",
            "nama_lengkap": "Budi Test",
            "jenis_kelamin": "Laki-Laki",
            "tanggal_lahir": "2000-05-15",
            "domisili": "Salatiga",
            "status_jemaat": "Jemaat",
            "status_diakonia": "Ya",
            "kelompok_ibadah": "Youth"
        }
    )

    jemaat_id = create_response.json()["data"]["id"]

    response = client.delete(
        f"/jemaat/{jemaat_id}",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 204


# =========================================================
# STAFF
# =========================================================

def test_staff_can_get_jemaat(
    client,
    staff_token
):
    response = client.get(
        "/jemaat",
        headers={
            "Authorization": f"Bearer {staff_token}"
        }
    )

    assert response.status_code == 200


def test_staff_can_create_jemaat(
    client,
    staff_token
):
    response = client.post(
        "/jemaat",
        headers={
            "Authorization": f"Bearer {staff_token}"
        },
        json={
            "nama_panggilan": "Staff",
            "nama_lengkap": "Jemaat Staff",
            "jenis_kelamin": "Laki-Laki",
            "tanggal_lahir": "1995-01-10",
            "domisili": "Salatiga",
            "status_jemaat": "Jemaat",
            "status_diakonia": "Tidak",
            "kelompok_ibadah": "Kompak"
        }
    )

    assert response.status_code == 201


def test_staff_cannot_delete_jemaat(
    client,
    staff_token
):
    # Buat data dengan token staff
    create_response = client.post(
        "/jemaat",
        headers={
            "Authorization": f"Bearer {staff_token}"
        },
        json={
            "nama_panggilan": "Staff",
            "nama_lengkap": "Jemaat Staff",
            "jenis_kelamin": "Laki-Laki",
            "tanggal_lahir": "1995-01-10",
            "domisili": "Salatiga",
            "status_jemaat": "Jemaat",
            "status_diakonia": "Tidak",
            "kelompok_ibadah": "Kompak"
        }
    )

    jemaat_id = create_response.json()["data"]["id"]

    response = client.delete(
        f"/jemaat/{jemaat_id}",
        headers={
            "Authorization": f"Bearer {staff_token}"
        }
    )

    assert response.status_code == 403


# =========================================================
# VIEWER
# =========================================================

def test_viewer_can_get_jemaat(
    client,
    viewer_token
):
    response = client.get(
        "/jemaat",
        headers={
            "Authorization": f"Bearer {viewer_token}"
        }
    )

    assert response.status_code == 200


def test_viewer_cannot_create_jemaat(
    client,
    viewer_token
):
    response = client.post(
        "/jemaat",
        headers={
            "Authorization": f"Bearer {viewer_token}"
        },
        json={
            "nama_panggilan": "Viewer",
            "nama_lengkap": "Jemaat Viewer",
            "jenis_kelamin": "Perempuan",
            "tanggal_lahir": "2000-01-01",
            "domisili": "Salatiga",
            "status_jemaat": "Jemaat",
            "status_diakonia": "Tidak",
            "kelompok_ibadah": "Youth"
        }
    )

    assert response.status_code == 403


def test_viewer_cannot_update_jemaat(
    client,
    viewer_token
):
    response = client.put(
        "/jemaat/999999",
        headers={
            "Authorization": f"Bearer {viewer_token}"
        },
        json={
            "nama_panggilan": "Viewer",
            "nama_lengkap": "Jemaat Viewer",
            "jenis_kelamin": "Perempuan",
            "tanggal_lahir": "2000-01-01",
            "domisili": "Salatiga",
            "status_jemaat": "Jemaat",
            "status_diakonia": "Tidak",
            "kelompok_ibadah": "Youth"
        }
    )

    assert response.status_code == 403


def test_viewer_cannot_delete_jemaat(
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