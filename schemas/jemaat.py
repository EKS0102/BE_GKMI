from datetime import date
from enum import Enum

from pydantic import BaseModel


# =========================================================
# ENUM - PILIHAN JENIS KELAMIN
# =========================================================

class JenisKelamin(str, Enum):
    LAKI_LAKI = "Laki-Laki"
    PEREMPUAN = "Perempuan"


# =========================================================
# ENUM - PILIHAN STATUS JEMAAT
# =========================================================

class StatusJemaat(str, Enum):
    JEMAAT = "Jemaat"
    SIMPATISAN = "Simpatisan"
    TAMU = "Tamu"


# =========================================================
# ENUM - PILIHAN STATUS DIAKONIA
# =========================================================

class StatusDiakonia(str, Enum):
    YA = "Ya"
    TIDAK = "Tidak"


# =========================================================
# ENUM - PILIHAN KELOMPOK IBADAH
# =========================================================

class KelompokIbadah(str, Enum):
    SEKOLAH_MINGGU = "Sekolah Minggu"
    YOUTH = "Youth"
    KOMPAK = "Kompak"
    KOPER = "Koper"
    LANSIA = "Lansia"


# =========================================================
# ENUM - PILIHAN SORTING FIELD
# =========================================================

class SortBy(str, Enum):
    ID = "id"
    NAMA_PANGGILAN = "nama_panggilan"
    NAMA_LENGKAP = "nama_lengkap"
    TANGGAL_LAHIR = "tanggal_lahir"
    JENIS_KELAMIN = "jenis_kelamin"
    STATUS_JEMAAT = "status_jemaat"
    STATUS_DIAKONIA = "status_diakonia"
    KELOMPOK_IBADAH = "kelompok_ibadah"


# =========================================================
# ENUM - PILIHAN SORTING ORDER
# =========================================================

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


# =========================================================
# CREATE
# Digunakan saat POST /jemaat
# =========================================================

class JemaatCreate(BaseModel):
    nama_panggilan: str
    nama_lengkap: str
    jenis_kelamin: JenisKelamin
    tanggal_lahir: date
    domisili: str
    status_jemaat: StatusJemaat
    status_diakonia: StatusDiakonia
    kelompok_ibadah: KelompokIbadah


# =========================================================
# UPDATE
# Digunakan saat PUT /jemaat/{id}
# =========================================================

class JemaatUpdate(BaseModel):
    nama_panggilan: str
    nama_lengkap: str
    jenis_kelamin: JenisKelamin
    tanggal_lahir: date
    domisili: str
    status_jemaat: StatusJemaat
    status_diakonia: StatusDiakonia
    kelompok_ibadah: KelompokIbadah


# =========================================================
# RESPONSE
# Digunakan saat mengembalikan data jemaat
# =========================================================

class JemaatResponse(BaseModel):
    id: int
    nama_panggilan: str
    nama_lengkap: str
    jenis_kelamin: JenisKelamin
    tanggal_lahir: date
    domisili: str
    status_jemaat: StatusJemaat
    status_diakonia: StatusDiakonia
    kelompok_ibadah: KelompokIbadah

    class Config:
        from_attributes = True


# =========================================================
# RESPONSE SETELAH CREATE / UPDATE
# =========================================================

class JemaatMessageResponse(BaseModel):
    message: str
    data: JemaatResponse


# =========================================================
# BULK RESPONSE
# Digunakan untuk POST /jemaat/bulk
# =========================================================

class JemaatBulkMessageResponse(BaseModel):
    message: str
    total_created: int
    data: list[JemaatResponse]


# =========================================================
# PAGINATION RESPONSE
# Digunakan untuk GET /jemaat
# =========================================================

class JemaatPaginationResponse(BaseModel):
    items: list[JemaatResponse]
    page: int
    limit: int
    total: int
    total_pages: int