from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

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
# ROUTERS
# =========================================================

app.include_router(
    auth_router
)

app.include_router(
    jemaat_router
)