from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database.database import Base, engine, SessionLocal

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

from schemas.user import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    TokenResponse
)

from services.jemaat_service import (
    get_all_jemaat,
    get_jemaat_by_id,
    create_jemaat,
    create_jemaat_bulk,
    update_jemaat,
    delete_jemaat
)

from services.auth_service import (
    get_user_by_username,
    get_user_by_email,
    create_user
)

from auth.security import create_access_token

from auth.auth import (
    require_authenticated,
    require_staff,
    require_admin
)

from logger import logger

from pwdlib import PasswordHash


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="Presensi Jemaat API",
    description="Backend API untuk sistem Presensi Jemaat",
    version="1.0.0"
)


# =========================================================
# PASSWORD HASH
# =========================================================

password_hash = PasswordHash.recommended()


# =========================================================
# DATABASE
# =========================================================

# Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# =========================================================
# GLOBAL ERROR HANDLER
# =========================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):
    logger.exception(
        f"Internal Server Error - "
        f"{request.method} {request.url.path} - "
        f"{str(exc)}"
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "Internal Server Error"
        }
    )


# =========================================================
# HOME
# =========================================================

@app.get(
    "/",
    status_code=status.HTTP_200_OK
)
def home():
    logger.info(
        "Endpoint GET / dipanggil"
    )

    return {
        "message": "Presensi Jemaat API - berjalan"
    }


# =========================================================
# AUTH - REGISTER
# =========================================================

# =========================================================
# AUTH - REGISTER
# =========================================================

@app.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "description": "Username atau email sudah digunakan"
        },
        422: {
            "description": "Format email tidak valid"
        },
        500: {
            "description": "Internal Server Error"
        }
    }
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    logger.info(
        f"Registrasi user: {data.username}"
    )

    # =====================================================
    # CEK USERNAME
    # =====================================================

    existing_user = get_user_by_username(
        db,
        data.username
    )

    if existing_user is not None:
        logger.warning(
            f"Registrasi gagal, username sudah digunakan: "
            f"{data.username}"
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username sudah digunakan"
        )

    # =====================================================
    # CEK EMAIL
    # =====================================================

    email_value = str(data.email)

    existing_email = get_user_by_email(
        db,
        email_value
    )

    if existing_email is not None:
        logger.warning(
            f"Registrasi gagal, email sudah digunakan: "
            f"{email_value}"
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email sudah digunakan"
        )

    # =====================================================
    # HASH PASSWORD
    # =====================================================

    hashed_password = password_hash.hash(
        data.password
    )

    # =====================================================
    # CREATE USER
    # =====================================================

    try:
        user = create_user(
            db=db,
            username=data.username,
            password_hash=hashed_password,
            role=data.role.value,
            email=email_value
        )

    except IntegrityError:
        logger.exception(
            f"IntegrityError saat registrasi user: "
            f"{data.username}"
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username atau email sudah digunakan"
        )

    logger.info(
        f"User berhasil dibuat: {user.username}"
    )

    return user

# =========================================================
# AUTH - LOGIN
# =========================================================

@app.post(
    "/auth/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {
            "description": "Username atau password salah"
        },
        403: {
            "description": "User tidak aktif"
        },
        500: {
            "description": "Internal Server Error"
        }
    }
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    logger.info(
        f"Percobaan login username: {data.username}"
    )

    user = get_user_by_username(
        db,
        data.username
    )

    # Username tidak ditemukan
    if user is None:
        logger.warning(
            f"Login gagal, username tidak ditemukan: "
            f"{data.username}"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah"
        )

    # User tidak aktif
    if not user.is_active:
        logger.warning(
            f"Login ditolak, user tidak aktif: "
            f"{data.username}"
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User tidak aktif"
        )

    # Password salah
    if not password_hash.verify(
        data.password,
        user.password_hash
    ):
        logger.warning(
            f"Login gagal, password salah: "
            f"{data.username}"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah"
        )

    # Buat JWT
    access_token = create_access_token(
        {
            "sub": user.username,
            "role": user.role
        }
    )

    logger.info(
        f"Login berhasil untuk username: "
        f"{user.username}"
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# =========================================================
# JEMAAT - GET ALL
# Pagination + Search + Filter + Sorting
#
# ADMIN / STAFF / VIEWER
# =========================================================

@app.get(
    "/jemaat",
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

    db: Session = Depends(get_db),
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

    try:
        return get_all_jemaat(
            db=db,
            page=page,
            limit=limit,
            search=search,
            jenis_kelamin=jenis_kelamin,
            status_jemaat=status_jemaat,
            status_diakonia=status_diakonia,
            kelompok_ibadah=kelompok_ibadah,
            sort_by=sort_by,
            sort_order=sort_order
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
# JEMAAT - GET BY ID
#
# ADMIN / STAFF / VIEWER
# =========================================================

@app.get(
    "/jemaat/{jemaat_id}",
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
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_authenticated
    )
):
    logger.info(
        f"User {current_user['username']} "
        f"mencari jemaat dengan ID {jemaat_id}"
    )

    data = get_jemaat_by_id(
        db,
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
# JEMAAT - CREATE
#
# ADMIN / STAFF
# =========================================================

@app.post(
    "/jemaat",
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
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_staff
    )
):
    logger.info(
        f"User {current_user['username']} "
        f"menambahkan jemaat: "
        f"{jemaat.nama_lengkap}"
    )

    data = create_jemaat(
        db,
        jemaat
    )

    return {
        "message": "Jemaat berhasil ditambahkan",
        "data": data
    }


# =========================================================
# JEMAAT - BULK CREATE
#
# ADMIN / STAFF
# =========================================================

@app.post(
    "/jemaat/bulk",
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
    db: Session = Depends(get_db),
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
        data = create_jemaat_bulk(
            db,
            jemaat_list
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
# JEMAAT - UPDATE
#
# ADMIN / STAFF
# =========================================================

@app.put(
    "/jemaat/{jemaat_id}",
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
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_staff
    )
):
    logger.info(
        f"User {current_user['username']} "
        f"mengubah jemaat dengan ID {jemaat_id}"
    )

    data = update_jemaat(
        db,
        jemaat_id,
        jemaat
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
# JEMAAT - DELETE
#
# ADMIN SAJA
# =========================================================

@app.delete(
    "/jemaat/{jemaat_id}",
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
    db: Session = Depends(get_db),
    current_user: dict = Depends(
        require_admin
    )
):
    logger.info(
        f"User {current_user['username']} "
        f"menghapus jemaat dengan ID {jemaat_id}"
    )

    data = delete_jemaat(
        db,
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

    logger.info(
        f"Jemaat dengan ID {jemaat_id} "
        f"berhasil dihapus"
    )

    return None