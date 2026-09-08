from models.jemaat import Jemaat

from schemas.jemaat import (
    JemaatCreate,
    JemaatUpdate,
    JenisKelamin,
    StatusJemaat,
    StatusDiakonia,
    KelompokIbadah
)

from repositories.jemaat_repository import JemaatRepository


# =========================================================
# SERVICE JEMAAT
# =========================================================

class JemaatService:

    def __init__(
        self,
        repository: JemaatRepository
    ):
        self.repository = repository

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
        query = self.repository.get_query()

        # =================================================
        # SEARCH
        # =================================================

        if search:
            search_value = f"%{search}%"

            query = query.filter(
                Jemaat.nama_panggilan.ilike(search_value)
                | Jemaat.nama_lengkap.ilike(search_value)
            )

        # =================================================
        # FILTER JENIS KELAMIN
        # =================================================

        if jenis_kelamin:
            query = query.filter(
                Jemaat.jenis_kelamin == jenis_kelamin.value
            )

        # =================================================
        # FILTER STATUS JEMAAT
        # =================================================

        if status_jemaat:
            query = query.filter(
                Jemaat.status_jemaat == status_jemaat.value
            )

        # =================================================
        # FILTER STATUS DIAKONIA
        # =================================================

        if status_diakonia:
            query = query.filter(
                Jemaat.status_diakonia == status_diakonia.value
            )

        # =================================================
        # FILTER KELOMPOK IBADAH
        # =================================================

        if kelompok_ibadah:
            query = query.filter(
                Jemaat.kelompok_ibadah == kelompok_ibadah.value
            )

        # =================================================
        # WHITELIST SORTING
        # =================================================

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
                f"Field sorting '{sort_by}' "
                f"tidak diperbolehkan"
            )

        # =================================================
        # SORT ORDER
        # =================================================

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

        # =================================================
        # TOTAL
        # =================================================

        total = query.count()

        # =================================================
        # PAGINATION
        # =================================================

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
        return self.repository.get_by_id(
            jemaat_id
        )

    # =====================================================
    # CREATE
    # =====================================================

    def create_jemaat(
        self,
        jemaat: JemaatCreate
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
            self.repository.add(
                data_baru
            )

            self.repository.commit()

            self.repository.refresh(
                data_baru
            )

            return data_baru

        except Exception:
            self.repository.rollback()
            raise

    # =====================================================
    # BULK CREATE
    # =====================================================

    def create_jemaat_bulk(
        self,
        jemaat_list: list[JemaatCreate]
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
            self.repository.add_many(
                data_baru
            )

            self.repository.commit()

            self.repository.refresh_many(
                data_baru
            )

            return data_baru

        except Exception:
            self.repository.rollback()
            raise

    # =====================================================
    # UPDATE
    # =====================================================

    def update_jemaat(
        self,
        jemaat_id: int,
        jemaat: JemaatUpdate
    ):
        data = self.repository.get_by_id(
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

            self.repository.commit()

            self.repository.refresh(
                data
            )

            return data

        except Exception:
            self.repository.rollback()
            raise

    # =====================================================
    # DELETE
    # =====================================================

    def delete_jemaat(
        self,
        jemaat_id: int
    ):
        data = self.repository.get_by_id(
            jemaat_id
        )

        if data is None:
            return None

        try:
            self.repository.delete(
                data
            )

            self.repository.commit()

            return data

        except Exception:
            self.repository.rollback()
            raise