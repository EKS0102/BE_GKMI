from pydantic import BaseModel


# =========================================================
# REGISTER
# Digunakan saat POST /auth/register
# =========================================================

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "user"


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
# Password tidak dikembalikan
# =========================================================

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


# =========================================================
# TOKEN RESPONSE
# Digunakan setelah login berhasil
# =========================================================

class TokenResponse(BaseModel):
    access_token: str
    token_type: str