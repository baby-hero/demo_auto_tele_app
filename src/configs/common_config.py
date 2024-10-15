import os

from dotenv import load_dotenv

# Load the .env file
load_dotenv()


TELE_BOT_TOKEN = os.getenv("TELE_BOT_TOKEN", "")
TELE_BOT_GROUP_ID = os.getenv("TELE_BOT_GROUP_ID", "")

ADB_HOST = os.getenv("ADB_HOST", "localhost")
ADB_PORT = int(os.getenv("ADB_PORT", 5037))

GENYMOTION_PATH = os.getenv("GENYMOTION_PATH", "")


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOGFORMAT = os.getenv("LOGFORMAT", "[%(asctime)s] [%(levelname)s] %(message)s")
LOG_FILE = os.getenv("LOG_FILE_PATH", "logs/app.log")
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 10))


IGNORE_HOUR_RUN_LIST = [
    int(i) for i in os.getenv("IGNORE_HOUR_RUN_LIST", "").split(",")
]

UI_TIMEOUT = int(os.getenv("UI_TIMEOUT", "10"))


IMAGE_FOLDER_PATH = os.getenv("IMAGE_FOLDER_PATH", "images/")
