from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status
)

from sqlalchemy.exc import IntegrityError

from pwdlib import PasswordHash

from schemas.user import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest
)

from services.auth_service import AuthService

from dependencies import (
    get_auth_service
)

from logger import logger


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# =========================================================
# PASSWORD HASH
# =========================================================

password_hash = PasswordHash.recommended()


# =========================================================
# REGISTER
# =========================================================

@router.post(
    "/register",
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
    service: AuthService = Depends(
        get_auth_service
    )
):
    logger.info(
        f"Registrasi user: {data.username}"
    )

    # =====================================================
    # CEK USERNAME
    # =====================================================

    existing_user = service.get_user_by_username(
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

    existing_email = service.get_user_by_email(
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
        user = service.create_user(
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
# LOGIN
# =========================================================

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {
            "description": "Username atau password salah"
        },
        403: {
            "description": "User tidak aktif"
        },
        429: {
            "description": (
                "Terlalu banyak percobaan login"
            )
        },
        500: {
            "description": "Internal Server Error"
        }
    }
)
def login(
    data: LoginRequest,
    request: Request,
    service: AuthService = Depends(
        get_auth_service
    )
):
    logger.info(
        f"Percobaan login username: {data.username}"
    )

    # =====================================================
    # IP ADDRESS
    # =====================================================

    ip_address = None

    if request.client is not None:
        ip_address = request.client.host

    # =====================================================
    # LOGIN
    # =====================================================

    try:
        result = service.login(
            username=data.username,
            password=data.password,
            ip_address=ip_address
        )

    except IntegrityError:
        logger.exception(
            f"Gagal memproses login: "
            f"{data.username}"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal membuat session login"
        )

    # =====================================================
    # USER TIDAK AKTIF
    # =====================================================

    if result == "inactive":
        logger.warning(
            f"Login ditolak, user tidak aktif: "
            f"{data.username}"
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User tidak aktif"
        )

    # =====================================================
    # LOGIN TERLALU BANYAK
    # =====================================================

    if result == "locked":
        logger.warning(
            f"Login diblokir sementara: "
            f"{data.username}, "
            f"ip={ip_address}"
        )

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                "Terlalu banyak percobaan login. "
                "Silakan coba lagi nanti."
            )
        )

    # =====================================================
    # USERNAME / PASSWORD SALAH
    # =====================================================

    if result is None:
        logger.warning(
            f"Login gagal untuk username: "
            f"{data.username}"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah"
        )

    # =====================================================
    # LOGIN BERHASIL
    # =====================================================

    logger.info(
        f"Login berhasil untuk username: "
        f"{data.username}"
    )

    return result


# =========================================================
# REFRESH ACCESS TOKEN - ROTATION
# =========================================================

@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {
            "description": (
                "Refresh token tidak valid, "
                "expired, atau revoked"
            )
        },
        500: {
            "description": "Internal Server Error"
        }
    }
)
def refresh_access_token(
    data: RefreshTokenRequest,
    request: Request,
    service: AuthService = Depends(
        get_auth_service
    )
):
    logger.info(
        "Percobaan refresh access token"
    )

    # =====================================================
    # IP ADDRESS
    # =====================================================

    ip_address = None

    if request.client is not None:
        ip_address = request.client.host

    # =====================================================
    # REFRESH TOKEN ROTATION
    # =====================================================

    try:
        result = service.refresh_access_token(
            raw_refresh_token=data.refresh_token,
            ip_address=ip_address
        )

    except IntegrityError:
        logger.exception(
            "Gagal melakukan refresh token rotation"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal memperbarui session"
        )

    # =====================================================
    # TOKEN TIDAK VALID
    # =====================================================

    if result is None:
        logger.warning(
            "Refresh token tidak valid"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token tidak valid"
        )

    # =====================================================
    # BERHASIL
    # =====================================================

    logger.info(
        "Refresh token berhasil di-rotate"
    )

    return result


# =========================================================
# LOGOUT
# =========================================================

@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    responses={
        401: {
            "description": "Refresh token tidak valid"
        },
        500: {
            "description": "Internal Server Error"
        }
    }
)
def logout(
    data: RefreshTokenRequest,
    service: AuthService = Depends(
        get_auth_service
    )
):
    logger.info(
        "Percobaan logout"
    )

    # =====================================================
    # REVOKE REFRESH TOKEN
    # =====================================================

    try:
        result = service.revoke_refresh_token(
            data.refresh_token
        )

    except IntegrityError:
        logger.exception(
            "Gagal melakukan revoke refresh token"
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal melakukan logout"
        )

    # =====================================================
    # TOKEN TIDAK VALID
    # =====================================================

    if not result:
        logger.warning(
            "Logout gagal, refresh token tidak valid"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token tidak valid"
        )

    # =====================================================
    # BERHASIL
    # =====================================================

    logger.info(
        "Logout berhasil"
    )

    return {
        "message": "Logout berhasil"
    }