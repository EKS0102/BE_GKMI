from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr


# =========================================================
# ENUM - PILIHAN ROLE USER
# =========================================================

class UserRole(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"
    VIEWER = "viewer"


# =========================================================
# REGISTER
# Digunakan saat POST /auth/register
# =========================================================

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: UserRole = UserRole.VIEWER
    email: EmailStr


# =========================================================
# LOGIN
# Digunakan saat POST /auth/login
# =========================================================

class LoginRequest(BaseModel):
    username: str
    password: str


# =========================================================
# USER RESPONSE
# Data user yang boleh dikirim ke client
# Password dan password_hash tidak dikembalikan
# =========================================================

class UserResponse(BaseModel):
    id: int
    username: str
    role: UserRole
    is_active: bool
    email: EmailStr | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================================================
# TOKEN RESPONSE
# Digunakan setelah login berhasil
# =========================================================

class TokenResponse(BaseModel):
    access_token: str
    token_type: str