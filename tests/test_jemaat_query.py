# =========================================================
# DATA TEST
# =========================================================

JEMAAT_DATA = [
    {
        "nama_panggilan": "Andi",
        "nama_lengkap": "Andi Setiawan",
        "jenis_kelamin": "Laki-Laki",
        "tanggal_lahir": "1995-01-10",
        "domisili": "Jl. Diponegoro No. 10, Salatiga",
        "status_jemaat": "Jemaat",
        "status_diakonia": "Ya",
        "kelompok_ibadah": "Youth"
    },
    {
        "nama_panggilan": "Maria",
        "nama_lengkap": "Maria Magdalena",
        "jenis_kelamin": "Perempuan",
        "tanggal_lahir": "1998-03-20",
        "domisili": "Jl. Pattimura No. 20, Salatiga",
        "status_jemaat": "Jemaat",
        "status_diakonia": "Tidak",
        "kelompok_ibadah": "Kompak"
    },
    {
        "nama_panggilan": "Budi",
        "nama_lengkap": "Budi Santoso",
        "jenis_kelamin": "Laki-Laki",
        "tanggal_lahir": "2000-05-15",
        "domisili": "Jl. Diponegoro No. 30, Salatiga",
        "status_jemaat": "Simpatisan",
        "status_diakonia": "Ya",
        "kelompok_ibadah": "Koper"
    },
    {
        "nama_panggilan": "Sari",
        "nama_lengkap": "Sari Wulandari",
        "jenis_kelamin": "Perempuan",
        "tanggal_lahir": "2002-07-12",
        "domisili": "Jl. Hasanudin No. 12, Salatiga",
        "status_jemaat": "Jemaat",
        "status_diakonia": "Ya",
        "kelompok_ibadah": "Youth"
    },
    {
        "nama_panggilan": "Tono",
        "nama_lengkap": "Tono Wijaya",
        "jenis_kelamin": "Laki-Laki",
        "tanggal_lahir": "1970-09-14",
        "domisili": "Jl. Sisingamangaraja No. 9, Salatiga",
        "status_jemaat": "Simpatisan",
        "status_diakonia": "Tidak",
        "kelompok_ibadah": "Lansia"
    }
]


# =========================================================
# HELPER BULK INSERT
# =========================================================

def insert_test_data(
    client,
    token
):
    response = client.post(
        "/jemaat/bulk",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=JEMAAT_DATA
    )

    assert response.status_code == 201

    return response.json()


# =========================================================
# PAGINATION
# =========================================================

def test_pagination(
    client,
    admin_token
):
    insert_test_data(
        client,
        admin_token
    )

    response = client.get(
        "/jemaat?page=1&limit=2",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 1
    assert data["limit"] == 2
    assert data["total"] == 5
    assert data["total_pages"] == 3
    assert len(data["items"]) == 2


# =========================================================
# PAGINATION PAGE 2
# =========================================================

def test_pagination_page_2(
    client,
    admin_token
):
    insert_test_data(
        client,
        admin_token
    )

    response = client.get(
        "/jemaat?page=2&limit=2",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 2
    assert data["limit"] == 2
    assert len(data["items"]) == 2


# =========================================================
# SEARCH
# =========================================================

def test_search_nama(
    client,
    admin_token
):
    insert_test_data(
        client,
        admin_token
    )

    response = client.get(
        "/jemaat?search=maria",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["total_pages"] == 1

    assert (
        data["items"][0]["nama_lengkap"]
        == "Maria Magdalena"
    )


# =========================================================
# SEARCH CASE INSENSITIVE
# =========================================================

def test_search_case_insensitive(
    client,
    admin_token
):
    insert_test_data(
        client,
        admin_token
    )

    response = client.get(
        "/jemaat?search=MARIA",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1


# =========================================================
# FILTER JENIS KELAMIN
# =========================================================

def test_filter_jenis_kelamin(
    client,
    admin_token
):
    insert_test_data(
        client,
        admin_token
    )

    response = client.get(
        "/jemaat?jenis_kelamin=Perempuan",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2

    for item in data["items"]:
        assert item["jenis_kelamin"] == "Perempuan"


# =========================================================
# FILTER STATUS JEMAAT
# =========================================================

def test_filter_status_jemaat(
    client,
    admin_token
):
    insert_test_data(
        client,
        admin_token
    )

    response = client.get(
        "/jemaat?status_jemaat=Jemaat",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 3

    for item in data["items"]:
        assert item["status_jemaat"] == "Jemaat"


# =========================================================
# FILTER STATUS DIAKONIA
# =========================================================

def test_filter_status_diakonia(
    client,
    admin_token
):
    insert_test_data(
        client,
        admin_token
    )

    response = client.get(
        "/jemaat?status_diakonia=Ya",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 3

    for item in data["items"]:
        assert item["status_diakonia"] == "Ya"


# =========================================================
# FILTER KELOMPOK IBADAH
# =========================================================

def test_filter_kelompok_ibadah(
    client,
    admin_token
):
    insert_test_data(
        client,
        admin_token
    )

    response = client.get(
        "/jemaat?kelompok_ibadah=Youth",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2

    for item in data["items"]:
        assert item["kelompok_ibadah"] == "Youth"


# =========================================================
# FILTER GABUNGAN
# =========================================================

def test_combined_filter(
    client,
    admin_token
):
    insert_test_data(
        client,
        admin_token
    )

    response = client.get(
        "/jemaat"
        "?jenis_kelamin=Perempuan"
        "&status_jemaat=Jemaat"
        "&status_diakonia=Ya"
        "&kelompok_ibadah=Youth",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1

    item = data["items"][0]

    assert item["nama_lengkap"] == "Sari Wulandari"


# =========================================================
# SORT ASC
# =========================================================

def test_sort_nama_asc(
    client,
    admin_token
):
    insert_test_data(
        client,
        admin_token
    )

    response = client.get(
        "/jemaat"
        "?sort_by=nama_lengkap"
        "&sort_order=asc",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    names = [
        item["nama_lengkap"]
        for item in data["items"]
    ]

    assert names == sorted(names)


# =========================================================
# SORT DESC
# =========================================================

def test_sort_nama_desc(
    client,
    admin_token
):
    insert_test_data(
        client,
        admin_token
    )

    response = client.get(
        "/jemaat"
        "?sort_by=nama_lengkap"
        "&sort_order=desc",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    names = [
        item["nama_lengkap"]
        for item in data["items"]
    ]

    assert names == sorted(
        names,
        reverse=True
    )


# =========================================================
# SORT TANGGAL LAHIR
# =========================================================

def test_sort_tanggal_lahir_asc(
    client,
    admin_token
):
    insert_test_data(
        client,
        admin_token
    )

    response = client.get(
        "/jemaat"
        "?sort_by=tanggal_lahir"
        "&sort_order=asc",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    dates = [
        item["tanggal_lahir"]
        for item in data["items"]
    ]

    assert dates == sorted(dates)


# =========================================================
# INVALID SORT FIELD
# =========================================================

def test_invalid_sort_by(
    client,
    admin_token
):
    response = client.get(
        "/jemaat?sort_by=nama_salah",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 422


# =========================================================
# INVALID SORT ORDER
# =========================================================

def test_invalid_sort_order(
    client,
    admin_token
):
    response = client.get(
        "/jemaat?sort_order=ascending",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 422


# =========================================================
# INVALID FILTER
# =========================================================

def test_invalid_jenis_kelamin(
    client,
    admin_token
):
    response = client.get(
        "/jemaat?jenis_kelamin=Semua",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 422


# =========================================================
# BULK INSERT
# =========================================================

def test_bulk_insert(
    client,
    admin_token
):
    response = client.post(
        "/jemaat/bulk",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json=JEMAAT_DATA
    )

    assert response.status_code == 201

    data = response.json()

    assert data["message"] == (
        "Data jemaat berhasil ditambahkan"
    )

    assert data["total_created"] == 5

    assert len(data["data"]) == 5


# =========================================================
# SEARCH + FILTER + PAGINATION + SORT
# =========================================================

def test_query_combination(
    client,
    admin_token
):
    insert_test_data(
        client,
        admin_token
    )

    response = client.get(
        "/jemaat"
        "?page=1"
        "&limit=1"
        "&search=a"
        "&jenis_kelamin=Perempuan"
        "&status_jemaat=Jemaat"
        "&sort_by=nama_lengkap"
        "&sort_order=asc",
        headers={
            "Authorization": f"Bearer {admin_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 1
    assert data["limit"] == 1
    assert data["total"] >= 1
    assert len(data["items"]) <= 1