from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS

from logger import logger

from routers.auth import router as auth_router
from routers.jemaat import router as jemaat_router


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="Presensi Jemaat API",
    description="Backend API untuk sistem Presensi Jemaat",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "OPTIONS"
    ],
    allow_headers=[
        "Authorization",
        "Content-Type"
    ]
)


# =========================================================
# SECURITY HEADERS
# =========================================================

@app.middleware("http")
async def security_headers_middleware(
    request: Request,
    call_next
):
    response = await call_next(
        request
    )

    response.headers[
        "X-Content-Type-Options"
    ] = "nosniff"

    response.headers[
        "X-Frame-Options"
    ] = "DENY"

    response.headers[
        "Referrer-Policy"
    ] = "strict-origin-when-cross-origin"

    response.headers[
        "Permissions-Policy"
    ] = (
        "camera=(), "
        "microphone=(), "
        "geolocation=()"
    )

    return response


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
        status_code=500,
        content={
            "message": "Internal Server Error"
        }
    )


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():
    logger.info(
        "Endpoint GET / dipanggil"
    )

    return {
        "message": "Presensi Jemaat API - berjalan"
    }


# =========================================================
# REGISTER ROUTERS
# =========================================================

app.include_router(
    auth_router
)

app.include_router(
    jemaat_router
)