from datetime import date
from unittest.mock import Mock

from models.jemaat import Jemaat

from schemas.jemaat import (
    JemaatCreate,
    JemaatUpdate,
    JenisKelamin,
    StatusJemaat,
    StatusDiakonia,
    KelompokIbadah
)

from services.jemaat_service import JemaatService


# =========================================================
# TEST DATA
# =========================================================

def create_jemaat_create():
    return JemaatCreate(
        nama_panggilan="Budi",
        nama_lengkap="Budi Santoso",
        jenis_kelamin=JenisKelamin.LAKI_LAKI,
        tanggal_lahir=date(2000, 5, 15),
        domisili="Salatiga",
        status_jemaat=StatusJemaat.JEMAAT,
        status_diakonia=StatusDiakonia.YA,
        kelompok_ibadah=KelompokIbadah.YOUTH
    )


def create_jemaat_update():
    return JemaatUpdate(
        nama_panggilan="Budi Update",
        nama_lengkap="Budi Santoso Update",
        jenis_kelamin=JenisKelamin.LAKI_LAKI,
        tanggal_lahir=date(2000, 5, 15),
        domisili="Semarang",
        status_jemaat=StatusJemaat.JEMAAT,
        status_diakonia=StatusDiakonia.TIDAK,
        kelompok_ibadah=KelompokIbadah.KOMPAK
    )


def create_model_jemaat():
    return Jemaat(
        id=1,
        nama_panggilan="Budi",
        nama_lengkap="Budi Santoso",
        jenis_kelamin="Laki-Laki",
        tanggal_lahir=date(2000, 5, 15),
        domisili="Salatiga",
        status_jemaat="Jemaat",
        status_diakonia="Ya",
        kelompok_ibadah="Youth"
    )


# =========================================================
# HELPER
# =========================================================

def create_service():

    repository = Mock()
    unit_of_work = Mock()

    service = JemaatService(
        repository,
        unit_of_work
    )

    return service, repository, unit_of_work


# =========================================================
# GET BY ID - FOUND
# =========================================================

def test_get_jemaat_by_id_found():

    service, repository, unit_of_work = (
        create_service()
    )

    expected = create_model_jemaat()

    repository.get_by_id.return_value = expected

    result = service.get_jemaat_by_id(1)

    assert result == expected

    repository.get_by_id.assert_called_once_with(
        1
    )


# =========================================================
# GET BY ID - NOT FOUND
# =========================================================

def test_get_jemaat_by_id_not_found():

    service, repository, unit_of_work = (
        create_service()
    )

    repository.get_by_id.return_value = None

    result = service.get_jemaat_by_id(999)

    assert result is None

    repository.get_by_id.assert_called_once_with(
        999
    )


# =========================================================
# CREATE
# =========================================================

def test_create_jemaat():

    service, repository, unit_of_work = (
        create_service()
    )

    result = service.create_jemaat(
        create_jemaat_create()
    )

    assert result is not None

    assert result.nama_panggilan == "Budi"
    assert result.nama_lengkap == "Budi Santoso"
    assert result.jenis_kelamin == "Laki-Laki"
    assert result.status_jemaat == "Jemaat"
    assert result.status_diakonia == "Ya"
    assert result.kelompok_ibadah == "Youth"

    repository.add.assert_called_once()

    unit_of_work.commit.assert_called_once()

    repository.refresh.assert_called_once_with(
        result
    )


# =========================================================
# UPDATE - FOUND
# =========================================================

def test_update_jemaat_found():

    service, repository, unit_of_work = (
        create_service()
    )

    existing_jemaat = create_model_jemaat()

    repository.get_by_id.return_value = (
        existing_jemaat
    )

    result = service.update_jemaat(
        1,
        create_jemaat_update()
    )

    assert result == existing_jemaat

    assert existing_jemaat.nama_panggilan == (
        "Budi Update"
    )

    assert existing_jemaat.nama_lengkap == (
        "Budi Santoso Update"
    )

    assert existing_jemaat.domisili == "Semarang"

    assert existing_jemaat.status_diakonia == "Tidak"

    assert existing_jemaat.kelompok_ibadah == "Kompak"

    repository.get_by_id.assert_called_once_with(
        1
    )

    unit_of_work.commit.assert_called_once()

    repository.refresh.assert_called_once_with(
        existing_jemaat
    )


# =========================================================
# UPDATE - NOT FOUND
# =========================================================

def test_update_jemaat_not_found():

    service, repository, unit_of_work = (
        create_service()
    )

    repository.get_by_id.return_value = None

    result = service.update_jemaat(
        999,
        create_jemaat_update()
    )

    assert result is None

    unit_of_work.commit.assert_not_called()

    unit_of_work.rollback.assert_not_called()


# =========================================================
# DELETE - FOUND
# =========================================================

def test_delete_jemaat_found():

    service, repository, unit_of_work = (
        create_service()
    )

    existing_jemaat = create_model_jemaat()

    repository.get_by_id.return_value = (
        existing_jemaat
    )

    result = service.delete_jemaat(1)

    assert result == existing_jemaat

    repository.get_by_id.assert_called_once_with(
        1
    )

    repository.delete.assert_called_once_with(
        existing_jemaat
    )

    unit_of_work.commit.assert_called_once()


# =========================================================
# DELETE - NOT FOUND
# =========================================================

def test_delete_jemaat_not_found():

    service, repository, unit_of_work = (
        create_service()
    )

    repository.get_by_id.return_value = None

    result = service.delete_jemaat(999)

    assert result is None

    repository.delete.assert_not_called()

    unit_of_work.commit.assert_not_called()


# =========================================================
# GET ALL
# =========================================================

def test_get_all_jemaat_repository_query():

    service, repository, unit_of_work = (
        create_service()
    )

    mock_query = Mock()

    repository.get_query.return_value = (
        mock_query
    )

    mock_query.filter.return_value = (
        mock_query
    )

    mock_query.order_by.return_value = (
        mock_query
    )

    mock_query.offset.return_value = (
        mock_query
    )

    mock_query.limit.return_value = (
        mock_query
    )

    mock_query.count.return_value = 0

    mock_query.all.return_value = []

    result = service.get_all_jemaat(
        page=1,
        limit=10
    )

    assert result["items"] == []
    assert result["page"] == 1
    assert result["limit"] == 10
    assert result["total"] == 0
    assert result["total_pages"] == 0

    repository.get_query.assert_called_once()
    
    
def test_create_jemaat_rollback_on_error():
    service, repository, unit_of_work = (
        create_service()
    )

    unit_of_work.commit.side_effect = Exception(
        "Database error"
    )

    try:
        service.create_jemaat(
            create_jemaat_create()
        )

        assert False, (
            "Exception seharusnya dilempar"
        )

    except Exception as exc:
        assert str(exc) == "Database error"

    repository.add.assert_called_once()

    unit_of_work.commit.assert_called_once()

    unit_of_work.rollback.assert_called_once()