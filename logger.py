import logging
import os

from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT
# =========================================================

load_dotenv()


# =========================================================
# KONFIGURASI LOGGING
# =========================================================

LOG_DIR = os.getenv(
    "LOG_DIR",
    "logs"
)

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO"
).upper()


# =========================================================
# VALIDASI LOG LEVEL
# =========================================================

VALID_LOG_LEVELS = {
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL"
}

if LOG_LEVEL not in VALID_LOG_LEVELS:
    raise ValueError(
        "LOG_LEVEL harus salah satu dari: "
        "DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )


# =========================================================
# LOG DIRECTORY
# =========================================================

os.makedirs(
    LOG_DIR,
    exist_ok=True
)


# =========================================================
# LOG FORMAT
# =========================================================

LOG_FORMAT = (
    "%(asctime)s - "
    "%(levelname)s - "
    "%(name)s - "
    "%(message)s"
)


# =========================================================
# ROOT LOGGING CONFIGURATION
# =========================================================

logging.basicConfig(
    level=getattr(
        logging,
        LOG_LEVEL
    ),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(
            os.path.join(
                LOG_DIR,
                "app.log"
            ),
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)


# =========================================================
# APPLICATION LOGGER
# =========================================================

logger = logging.getLogger(
    "BE-GKMI"
)