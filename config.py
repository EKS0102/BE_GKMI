import os

from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# ENVIRONMENT
# =========================================================

ENVIRONMENT = os.getenv(
    "ENVIRONMENT",
    "development"
).lower()


if ENVIRONMENT not in {
    "development",
    "production"
}:
    raise ValueError(
        "ENVIRONMENT harus development atau production"
    )


# =========================================================
# DATABASE
# =========================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL belum diset di file .env"
    )


# =========================================================
# TEST DATABASE
# =========================================================

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL"
)

if not TEST_DATABASE_URL:
    raise ValueError(
        "TEST_DATABASE_URL belum diset di file .env"
    )


# =========================================================
# JWT
# =========================================================

SECRET_KEY = os.getenv(
    "SECRET_KEY"
)

if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY belum diset di file .env"
    )


# =========================================================
# PRODUCTION SECRET VALIDATION
# =========================================================

if (
    ENVIRONMENT == "production"
    and (
        SECRET_KEY.startswith("YOUR_")
        or SECRET_KEY.startswith("docker-development-")
        or len(SECRET_KEY) < 32
    )
):
    raise ValueError(
        "SECRET_KEY production tidak aman. "
        "Gunakan secret yang kuat dan unik."
    )


ALGORITHM = os.getenv(
    "ALGORITHM",
    "HS256"
)


ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "60"
    )
)


# # =========================================================
# # CORS
# # =========================================================

# CORS_ORIGINS_RAW = os.getenv(
#     "CORS_ORIGINS",
#     "http://localhost:3000,http://localhost:5173"
# )

# CORS_ORIGINS = [
#     origin.strip()
#     for origin in CORS_ORIGINS_RAW.split(",")
#     if origin.strip()
# ]


# =========================================================
# CORS
# =========================================================

CORS_ORIGINS_RAW = os.getenv(
    "CORS_ORIGINS"
)

if (
    ENVIRONMENT == "production"
    and not CORS_ORIGINS_RAW
):
    raise ValueError(
        "CORS_ORIGINS wajib diset pada production"
    )


if not CORS_ORIGINS_RAW:
    CORS_ORIGINS_RAW = (
        "http://localhost:3000,"
        "http://localhost:5173"
    )


CORS_ORIGINS = [
    origin.strip()
    for origin in CORS_ORIGINS_RAW.split(",")
    if origin.strip()
]