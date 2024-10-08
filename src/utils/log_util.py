import logging
from logging.handlers import TimedRotatingFileHandler

from src.configs import LOG_BACKUP_COUNT, LOG_FILE, LOG_LEVEL, LOGFORMAT

# ---------------------------------------------#
# Set up formatter
formatter = logging.Formatter(LOGFORMAT, "%Y-%m-%d %H:%M:%S")

# Set up file handler with daily rotation
file_handler = TimedRotatingFileHandler(
    LOG_FILE, when="midnight", interval=1, backupCount=LOG_BACKUP_COUNT
)
file_handler.setFormatter(formatter)
file_handler.setLevel(LOG_LEVEL)

# Set up root logger
logging.root.setLevel(LOG_LEVEL)
logger = logging.getLogger("uiautomator2")
logger.setLevel(LOG_LEVEL)
logger.addHandler(file_handler)
# ---------------------------------------------#
