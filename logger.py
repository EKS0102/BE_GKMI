import logging
import os


LOG_DIR = "logs"

os.makedirs(LOG_DIR, exist_ok=True)


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"


logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(
            os.path.join(LOG_DIR, "app.log"),
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)


logger = logging.getLogger("BE-GKMI")