import sys
from os import makedirs

from loguru import logger

from src.config import LOG_LEVEL, LOG_TO_CONSOL, LOG_TO_FILE, LOGS_DIR, LOGS_FILE

# Ensure the logs directory exists
makedirs(LOGS_DIR, exist_ok=True)


def init_loguru() -> None:

    # Remove the default logger
    logger.remove()

    # Add file logger if LOG_TO_FILE is True
    if LOG_TO_FILE:
        logger.add(
            LOGS_FILE,
            level=LOG_LEVEL,
            rotation="10 MB",
            # retention="31 days",
            compression="zip",
        )

    # Add consol logger if LOG_TO_CONSOL is True
    if LOG_TO_CONSOL:
        logger.add(
            sys.stdout,
            level=LOG_LEVEL,
            colorize=True,
        )


init_loguru()

logger.info(f"Logger initialized successfully.")
