from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from routers.jemaat import (
    get_jemaat,
    create_jemaat_bulk_api,
)


def test_get_jemaat_invalid_page():
    service = MagicMock()

    current_user = {
        "id": 1,
        "username": "admin",
    }

    with pytest.raises(HTTPException) as exc_info:
        get_jemaat(
            page=0,
            limit=10,
            search=None,
            jenis_kelamin=None,
            status_jemaat=None,
            status_diakonia=None,
            kelompok_ibadah=None,
            sort_by=MagicMock(value="id"),
            sort_order=MagicMock(value="asc"),
            service=service,
            current_user=current_user,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "Page harus lebih besar atau sama dengan 1"
    )

    service.get_all_jemaat.assert_not_called()


def test_get_jemaat_invalid_limit():
    service = MagicMock()

    current_user = {
        "id": 1,
        "username": "admin",
    }

    with pytest.raises(HTTPException) as exc_info:
        get_jemaat(
            page=1,
            limit=101,
            search=None,
            jenis_kelamin=None,
            status_jemaat=None,
            status_diakonia=None,
            kelompok_ibadah=None,
            sort_by=MagicMock(value="id"),
            sort_order=MagicMock(value="asc"),
            service=service,
            current_user=current_user,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "Limit harus antara 1 sampai 100"
    )

    service.get_all_jemaat.assert_not_called()


def test_get_jemaat_service_value_error():
    service = MagicMock()

    service.get_all_jemaat.side_effect = ValueError(
        "Parameter sort tidak valid"
    )

    current_user = {
        "id": 1,
        "username": "admin",
    }

    with pytest.raises(HTTPException) as exc_info:
        get_jemaat(
            page=1,
            limit=10,
            search=None,
            jenis_kelamin=None,
            status_jemaat=None,
            status_diakonia=None,
            kelompok_ibadah=None,
            sort_by=MagicMock(value="id"),
            sort_order=MagicMock(value="asc"),
            service=service,
            current_user=current_user,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "Parameter sort tidak valid"
    )


def test_create_jemaat_bulk_empty():
    service = MagicMock()

    current_user = {
        "id": 1,
        "username": "admin",
    }

    with pytest.raises(HTTPException) as exc_info:
        create_jemaat_bulk_api(
            jemaat_list=[],
            service=service,
            current_user=current_user,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "Data jemaat tidak boleh kosong"
    )

    service.create_jemaat_bulk.assert_not_called()


def test_create_jemaat_bulk_service_exception():
    service = MagicMock()

    service.create_jemaat_bulk.side_effect = Exception(
        "database error"
    )

    current_user = {
        "id": 1,
        "username": "admin",
    }

    jemaat = MagicMock()

    with pytest.raises(HTTPException) as exc_info:
        create_jemaat_bulk_api(
            jemaat_list=[jemaat],
            service=service,
            current_user=current_user,
        )

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == (
        "Gagal menambahkan data jemaat"
    )