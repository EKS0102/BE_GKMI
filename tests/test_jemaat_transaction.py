from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from models.jemaat import Jemaat

from repositories.jemaat_repository import JemaatRepository
from repositories.audit_log_repository import AuditLogRepository

from schemas.jemaat import (
    JemaatCreate,
    JenisKelamin,
    StatusJemaat,
    StatusDiakonia,
    KelompokIbadah
)

from services.jemaat_service import JemaatService
from unit_of_work import UnitOfWork


# =========================================================
# TEST DATA
# =========================================================

def create_jemaat_data():

    return JemaatCreate(
        nama_panggilan="Rollback",
        nama_lengkap="Jemaat Rollback Test",
        jenis_kelamin=JenisKelamin.LAKI_LAKI,
        tanggal_lahir=date(2000, 1, 1),
        domisili="Salatiga",
        status_jemaat=StatusJemaat.JEMAAT,
        status_diakonia=StatusDiakonia.YA,
        kelompok_ibadah=KelompokIbadah.YOUTH
    )


# =========================================================
# CREATE UNIT OF WORK
# =========================================================

def create_service(db):

    unit_of_work = UnitOfWork(
        db
    )

    service = JemaatService(
        unit_of_work
    )

    return service


# =========================================================
# TRANSACTION - ROLLBACK
#
# Jemaat berhasil di-add dan di-flush.
# AuditLog menggunakan user_id yang tidak ada.
# Foreign key error terjadi.
# Transaction harus di-rollback.
# =========================================================

def test_create_jemaat_rollback_when_audit_log_fails(
    db
):
    service = create_service(
        db
    )

    # =====================================================
    # USER ID TIDAK ADA
    # =====================================================

    invalid_user_id = 999999

    # =====================================================
    # EXPECT INTEGRITY ERROR
    # =====================================================

    with pytest.raises(
        IntegrityError
    ):

        service.create_jemaat(
            jemaat=create_jemaat_data(),
            user_id=invalid_user_id,
            ip_address="127.0.0.1"
        )

    # =====================================================
    # PASTIKAN TRANSACTION SUDAH ROLLBACK
    # =====================================================

    # Service sudah memanggil rollback(),
    # sehingga session siap digunakan kembali.

    # =====================================================
    # CEK JEMAAT TIDAK TERSIMPAN
    # =====================================================

    result = (
        db.query(Jemaat)
        .filter(
            Jemaat.nama_lengkap
            == "Jemaat Rollback Test"
        )
        .first()
    )

    assert result is None


# =========================================================
# TRANSACTION - VALID USER
#
# Sebagai pembanding, kalau user valid maka:
# Jemaat + AuditLog berhasil.
# =========================================================

def test_create_jemaat_transaction_success(
    db,
    create_test_user
):
    service = create_service(
        db
    )

    result = service.create_jemaat(
        jemaat=create_jemaat_data(),
        user_id=create_test_user.id,
        ip_address="127.0.0.1"
    )

    assert result is not None

    assert result.id is not None

    # =====================================================
    # CEK JEMAAT BENAR-BENAR TERSIMPAN
    # =====================================================

    saved_jemaat = (
        db.query(Jemaat)
        .filter(
            Jemaat.id == result.id
        )
        .first()
    )

    assert saved_jemaat is not None

    assert (
        saved_jemaat.nama_lengkap
        == "Jemaat Rollback Test"
    )