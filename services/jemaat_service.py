from datetime import datetime, UTC

from schemas.jemaat import (
    JemaatCreate,
    JemaatUpdate,
    JenisKelamin,
    StatusJemaat,
    StatusDiakonia,
    KelompokIbadah
)

from models.jemaat import Jemaat
from models.audit_log import AuditLog

from unit_of_work import UnitOfWork


# =========================================================
# SERVICE JEMAAT
# =========================================================

class JemaatService:

    def __init__(
        self,
        unit_of_work: UnitOfWork
    ):
        self.unit_of_work = unit_of_work

    # =====================================================
    # GET SEMUA JEMAAT
    # Pagination + Search + Filter + Sorting
    # =====================================================

    def get_all_jemaat(
        self,
        page: int,
        limit: int,
        search: str | None = None,
        jenis_kelamin: JenisKelamin | None = None,
        status_jemaat: StatusJemaat | None = None,
        status_diakonia: StatusDiakonia | None = None,
        kelompok_ibadah: KelompokIbadah | None = None,
        sort_by: str = "id",
        sort_order: str = "asc"
    ):
        query = self.unit_of_work.jemaat.get_query()

        if search:
            search_value = f"%{search}%"

            query = query.filter(
                Jemaat.nama_panggilan.ilike(search_value)
                | Jemaat.nama_lengkap.ilike(search_value)
            )

        if jenis_kelamin:
            query = query.filter(
                Jemaat.jenis_kelamin == jenis_kelamin.value
            )

        if status_jemaat:
            query = query.filter(
                Jemaat.status_jemaat == status_jemaat.value
            )

        if status_diakonia:
            query = query.filter(
                Jemaat.status_diakonia == status_diakonia.value
            )

        if kelompok_ibadah:
            query = query.filter(
                Jemaat.kelompok_ibadah == kelompok_ibadah.value
            )

        allowed_sort_fields = {
            "id": Jemaat.id,
            "nama_panggilan": Jemaat.nama_panggilan,
            "nama_lengkap": Jemaat.nama_lengkap,
            "tanggal_lahir": Jemaat.tanggal_lahir,
            "jenis_kelamin": Jemaat.jenis_kelamin,
            "status_jemaat": Jemaat.status_jemaat,
            "status_diakonia": Jemaat.status_diakonia,
            "kelompok_ibadah": Jemaat.kelompok_ibadah
        }

        sort_column = allowed_sort_fields.get(
            sort_by
        )

        if sort_column is None:
            raise ValueError(
                f"Field sorting '{sort_by}' tidak diperbolehkan"
            )

        if sort_order == "asc":
            query = query.order_by(
                sort_column.asc()
            )

        elif sort_order == "desc":
            query = query.order_by(
                sort_column.desc()
            )

        else:
            raise ValueError(
                "sort_order harus 'asc' atau 'desc'"
            )

        total = query.count()

        offset = (page - 1) * limit

        items = (
            query
            .offset(offset)
            .limit(limit)
            .all()
        )

        total_pages = (
            (total + limit - 1) // limit
        )

        return {
            "items": items,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages
        }

    # =====================================================
    # GET BY ID
    # =====================================================

    def get_jemaat_by_id(
        self,
        jemaat_id: int
    ):
        return self.unit_of_work.jemaat.get_by_id(
            jemaat_id
        )

    # =====================================================
    # CREATE JEMAAT + AUDIT LOG
    # =====================================================

    def create_jemaat(
        self,
        jemaat: JemaatCreate,
        user_id: int | None = None,
        ip_address: str | None = None
    ):
        data_baru = Jemaat(
            nama_panggilan=jemaat.nama_panggilan,
            nama_lengkap=jemaat.nama_lengkap,
            jenis_kelamin=jemaat.jenis_kelamin.value,
            tanggal_lahir=jemaat.tanggal_lahir,
            domisili=jemaat.domisili,
            status_jemaat=jemaat.status_jemaat.value,
            status_diakonia=jemaat.status_diakonia.value,
            kelompok_ibadah=jemaat.kelompok_ibadah.value
        )

        try:
            # =================================================
            # 1. ADD JEMAAT
            # =================================================

            self.unit_of_work.jemaat.add(
                data_baru
            )

            # =================================================
            # 2. FLUSH
            # =================================================
            #
            # Kita membutuhkan ID Jemaat sebelum membuat
            # AuditLog.
            #
            # Flush mengirim INSERT ke database tanpa
            # melakukan COMMIT.
            #

            self.unit_of_work.session.flush()

            # =================================================
            # 3. ADD AUDIT LOG
            # =================================================

            if user_id is not None:
                audit_log = AuditLog(
                    user_id=user_id,
                    action="CREATE",
                    resource="jemaat",
                    resource_id=data_baru.id,
                    description=(
                        f"Menambahkan data jemaat "
                        f"{data_baru.nama_lengkap}"
                    ),
                    ip_address=ip_address,
                    created_at=datetime.now(UTC)
                )

                self.unit_of_work.audit_log.add(
                    audit_log
                )

            # =================================================
            # 4. COMMIT SEMUA
            # =================================================

            self.unit_of_work.commit()

            # =================================================
            # 5. REFRESH
            # =================================================

            self.unit_of_work.jemaat.refresh(
                data_baru
            )

            return data_baru

        except Exception:
            self.unit_of_work.rollback()
            raise

    # =====================================================
    # BULK CREATE
    # =====================================================

    def create_jemaat_bulk(
        self,
        jemaat_list: list[JemaatCreate],
        user_id: int | None = None,
        ip_address: str | None = None
    ):
        data_baru = []

        for jemaat in jemaat_list:
            data = Jemaat(
                nama_panggilan=jemaat.nama_panggilan,
                nama_lengkap=jemaat.nama_lengkap,
                jenis_kelamin=jemaat.jenis_kelamin.value,
                tanggal_lahir=jemaat.tanggal_lahir,
                domisili=jemaat.domisili,
                status_jemaat=jemaat.status_jemaat.value,
                status_diakonia=jemaat.status_diakonia.value,
                kelompok_ibadah=jemaat.kelompok_ibadah.value
            )

            data_baru.append(data)

        try:
            # =================================================
            # ADD SEMUA JEMAAT
            # =================================================

            self.unit_of_work.jemaat.add_many(
                data_baru
            )

            # =================================================
            # FLUSH
            # =================================================

            self.unit_of_work.session.flush()

            # =================================================
            # ADD AUDIT LOG
            # =================================================

            if user_id is not None:
                for data in data_baru:

                    audit_log = AuditLog(
                        user_id=user_id,
                        action="CREATE",
                        resource="jemaat",
                        resource_id=data.id,
                        description=(
                            f"Menambahkan data jemaat "
                            f"{data.nama_lengkap}"
                        ),
                        ip_address=ip_address,
                        created_at=datetime.now(UTC)
                    )

                    self.unit_of_work.audit_log.add(
                        audit_log
                    )

            # =================================================
            # COMMIT
            # =================================================

            self.unit_of_work.commit()

            # =================================================
            # REFRESH
            # =================================================

            self.unit_of_work.jemaat.refresh_many(
                data_baru
            )

            return data_baru

        except Exception:
            self.unit_of_work.rollback()
            raise

    # =====================================================
    # UPDATE
    # =====================================================

    def update_jemaat(
        self,
        jemaat_id: int,
        jemaat: JemaatUpdate,
        user_id: int | None = None,
        ip_address: str | None = None
    ):
        data = self.unit_of_work.jemaat.get_by_id(
            jemaat_id
        )

        if data is None:
            return None

        try:
            data.nama_panggilan = (
                jemaat.nama_panggilan
            )

            data.nama_lengkap = (
                jemaat.nama_lengkap
            )

            data.jenis_kelamin = (
                jemaat.jenis_kelamin.value
            )

            data.tanggal_lahir = (
                jemaat.tanggal_lahir
            )

            data.domisili = (
                jemaat.domisili
            )

            data.status_jemaat = (
                jemaat.status_jemaat.value
            )

            data.status_diakonia = (
                jemaat.status_diakonia.value
            )

            data.kelompok_ibadah = (
                jemaat.kelompok_ibadah.value
            )

            # =================================================
            # FLUSH UPDATE
            # =================================================

            self.unit_of_work.session.flush()

            # =================================================
            # AUDIT LOG
            # =================================================

            if user_id is not None:
                audit_log = AuditLog(
                    user_id=user_id,
                    action="UPDATE",
                    resource="jemaat",
                    resource_id=data.id,
                    description=(
                        f"Memperbarui data jemaat "
                        f"{data.nama_lengkap}"
                    ),
                    ip_address=ip_address,
                    created_at=datetime.now(UTC)
                )

                self.unit_of_work.audit_log.add(
                    audit_log
                )

            # =================================================
            # COMMIT
            # =================================================

            self.unit_of_work.commit()

            self.unit_of_work.jemaat.refresh(
                data
            )

            return data

        except Exception:
            self.unit_of_work.rollback()
            raise

    # =====================================================
    # DELETE
    # =====================================================

    def delete_jemaat(
        self,
        jemaat_id: int,
        user_id: int | None = None,
        ip_address: str | None = None
    ):
        data = self.unit_of_work.jemaat.get_by_id(
            jemaat_id
        )

        if data is None:
            return None

        try:
            # =================================================
            # AUDIT LOG SEBELUM DELETE
            # =================================================
            #
            # Data Jemaat masih ada sehingga nama lengkap
            # masih bisa digunakan dalam description.
            #

            if user_id is not None:
                audit_log = AuditLog(
                    user_id=user_id,
                    action="DELETE",
                    resource="jemaat",
                    resource_id=data.id,
                    description=(
                        f"Menghapus data jemaat "
                        f"{data.nama_lengkap}"
                    ),
                    ip_address=ip_address,
                    created_at=datetime.now(UTC)
                )

                self.unit_of_work.audit_log.add(
                    audit_log
                )

            # =================================================
            # DELETE JEMAAT
            # =================================================

            self.unit_of_work.jemaat.delete(
                data
            )

            # =================================================
            # COMMIT
            # =================================================

            self.unit_of_work.commit()

            return data

        except Exception:
            self.unit_of_work.rollback()
            raise