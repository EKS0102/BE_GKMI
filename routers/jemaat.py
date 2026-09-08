from fastapi import APIRouter, Depends, HTTPException, status

from schemas.jemaat import (
    JemaatCreate,
    JemaatUpdate,
    JemaatResponse,
    JemaatMessageResponse,
    JemaatPaginationResponse,
    JemaatBulkMessageResponse,
    JenisKelamin,
    StatusJemaat,
    StatusDiakonia,
    KelompokIbadah,
    SortBy,
    SortOrder
)

from services.jemaat_service import JemaatService

from dependencies import (
    get_jemaat_service
)

from auth.auth import (
    require_authenticated,
    require_staff,
    require_admin
)

from logger import logger


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/jemaat",
    tags=["Jemaat"]
)


# =========================================================
# GET ALL JEMAAT
# Pagination + Search + Filter + Sorting
# ADMIN / STAFF / VIEWER
# =========================================================

@router.get(
    "",
    response_model=JemaatPaginationResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description": "Parameter pagination tidak valid"
        },
        401: {
            "description": "Token tidak valid atau tidak ada"
        },
        403: {
            "description": "Tidak memiliki izin"
        },
        500: {
            "description": "Internal Server Error"
        }
    }
)
def get_jemaat(
    page: int = 1,
    limit: int = 10,
    search: str | None = None,
    jenis_kelamin: JenisKelamin | None = None,
    status_jemaat: StatusJemaat | None = None,
    status_diakonia: StatusDiakonia | None = None,
    kelompok_ibadah: KelompokIbadah | None = None,
    sort_by: SortBy = SortBy.ID,
    sort_order: SortOrder = SortOrder.ASC,
    service: JemaatService = Depends(
        get_jemaat_service
    ),
    current_user: dict = Depends(
        require_authenticated
    )
):
    # =====================================================
    # VALIDASI PAGINATION
    # =====================================================

    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page harus lebih besar atau sama dengan 1"
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit harus antara 1 sampai 100"
        )

    # =====================================================
    # LOG
    # =====================================================

    logger.info(
        f"User {current_user['username']} "
        f"mengambil data jemaat "
        f"page={page}, "
        f"limit={limit}, "
        f"search={search}, "
        f"jenis_kelamin={jenis_kelamin}, "
        f"status_jemaat={status_jemaat}, "
        f"status_diakonia={status_diakonia}, "
        f"kelompok_ibadah={kelompok_ibadah}, "
        f"sort_by={sort_by.value}, "
        f"sort_order={sort_order.value}"
    )

    # =====================================================
    # SERVICE
    # =====================================================

    try:
        return service.get_all_jemaat(
            page=page,
            limit=limit,
            search=search,
            jenis_kelamin=jenis_kelamin,
            status_jemaat=status_jemaat,
            status_diakonia=status_diakonia,
            kelompok_ibadah=kelompok_ibadah,
            sort_by=sort_by.value,
            sort_order=sort_order.value
        )

    except ValueError as exc:
        logger.warning(
            f"Parameter query tidak valid: {str(exc)}"
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )


# =========================================================
# GET JEMAAT BY ID
# ADMIN / STAFF / VIEWER
# =========================================================

@router.get(
    "/{jemaat_id}",
    response_model=JemaatResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {
            "description": "Token tidak valid atau tidak ada"
        },
        403: {
            "description": "Tidak memiliki izin"
        },
        404: {
            "description": "Jemaat tidak ditemukan"
        },
        500: {
            "description": "Internal Server Error"
        }
    }
)
def get_jemaat_detail(
    jemaat_id: int,
    service: JemaatService = Depends(
        get_jemaat_service
    ),
    current_user: dict = Depends(
        require_authenticated
    )
):
    logger.info(
        f"User {current_user['username']} "
        f"mencari jemaat dengan ID {jemaat_id}"
    )

    data = service.get_jemaat_by_id(
        jemaat_id
    )

    if data is None:
        logger.warning(
            f"Jemaat dengan ID {jemaat_id} "
            f"tidak ditemukan"
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jemaat tidak ditemukan"
        )

    return data


# =========================================================
# CREATE JEMAAT
# ADMIN / STAFF
# =========================================================

@router.post(
    "",
    response_model=JemaatMessageResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "description": "Data tidak valid"
        },
        401: {
            "description": "Token tidak valid atau tidak ada"
        },
        403: {
            "description": "Hanya admin atau staff"
        },
        500: {
            "description": "Internal Server Error"
        }
    }
)
def create_jemaat_api(
    jemaat: JemaatCreate,
    service: JemaatService = Depends(
        get_jemaat_service
    ),
    current_user: dict = Depends(
        require_staff
    )
):
    logger.info(
        f"User {current_user['username']} "
        f"menambahkan jemaat: "
        f"{jemaat.nama_lengkap}"
    )

    data = service.create_jemaat(
        jemaat,
        user_id=current_user.get("id"),
        ip_address=None
    )

    return {
        "message": "Jemaat berhasil ditambahkan",
        "data": data
    }


# =========================================================
# BULK CREATE JEMAAT
# ADMIN / STAFF
# =========================================================

@router.post(
    "/bulk",
    response_model=JemaatBulkMessageResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "description": "Data jemaat kosong atau tidak valid"
        },
        401: {
            "description": "Token tidak valid atau tidak ada"
        },
        403: {
            "description": "Hanya admin atau staff"
        },
        500: {
            "description": "Internal Server Error"
        }
    }
)
def create_jemaat_bulk_api(
    jemaat_list: list[JemaatCreate],
    service: JemaatService = Depends(
        get_jemaat_service
    ),
    current_user: dict = Depends(
        require_staff
    )
):
    # =====================================================
    # CEK DATA KOSONG
    # =====================================================

    if not jemaat_list:
        logger.warning(
            f"User {current_user['username']} "
            f"mengirim bulk insert kosong"
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data jemaat tidak boleh kosong"
        )

    logger.info(
        f"User {current_user['username']} "
        f"melakukan bulk insert "
        f"{len(jemaat_list)} data jemaat"
    )

    try:
        data = service.create_jemaat_bulk(
            jemaat_list,
            user_id=current_user.get("id"),
            ip_address=None
        )

        logger.info(
            f"Bulk insert berhasil: "
            f"{len(data)} data jemaat"
        )

        return {
            "message": "Data jemaat berhasil ditambahkan",
            "total_created": len(data),
            "data": data
        }

    except Exception as exc:
        logger.exception(
            f"Bulk insert jemaat gagal: {str(exc)}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal menambahkan data jemaat"
        )


# =========================================================
# UPDATE JEMAAT
# ADMIN / STAFF
# =========================================================

@router.put(
    "/{jemaat_id}",
    response_model=JemaatMessageResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {
            "description": "Token tidak valid atau tidak ada"
        },
        403: {
            "description": "Hanya admin atau staff"
        },
        404: {
            "description": "Jemaat tidak ditemukan"
        },
        500: {
            "description": "Internal Server Error"
        }
    }
)
def update_jemaat_api(
    jemaat_id: int,
    jemaat: JemaatUpdate,
    service: JemaatService = Depends(
        get_jemaat_service
    ),
    current_user: dict = Depends(
        require_staff
    )
):
    logger.info(
        f"User {current_user['username']} "
        f"mengubah jemaat dengan ID {jemaat_id}"
    )

    data = service.update_jemaat(
        jemaat_id,
        jemaat,
        user_id=current_user.get("id"),
        ip_address=None
    )

    if data is None:
        logger.warning(
            f"Jemaat dengan ID {jemaat_id} "
            f"tidak ditemukan"
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jemaat tidak ditemukan"
        )

    return {
        "message": "Jemaat berhasil diperbarui",
        "data": data
    }


# =========================================================
# DELETE JEMAAT
# ADMIN SAJA
# =========================================================

@router.delete(
    "/{jemaat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {
            "description": "Token tidak valid atau tidak ada"
        },
        403: {
            "description": "Hanya admin"
        },
        404: {
            "description": "Jemaat tidak ditemukan"
        },
        500: {
            "description": "Internal Server Error"
        }
    }
)
def delete_jemaat_api(
    jemaat_id: int,
    service: JemaatService = Depends(
        get_jemaat_service
    ),
    current_user: dict = Depends(
        require_admin
    )
):
    logger.info(
        f"User {current_user['username']} "
        f"menghapus jemaat dengan ID {jemaat_id}"
    )

    data = service.delete_jemaat(
        jemaat_id,
        user_id=current_user.get("id"),
        ip_address=None
    )

    if data is None:
        logger.warning(
            f"Jemaat dengan ID {jemaat_id} "
            f"tidak ditemukan"
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Jemaat tidak ditemukan"
        )

    logger.info(
        f"Jemaat dengan ID {jemaat_id} "
        f"berhasil dihapus"
    )

    return None