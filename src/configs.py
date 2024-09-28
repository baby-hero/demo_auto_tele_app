import os

from dotenv import load_dotenv

# Load the .env file
load_dotenv()

IGNORE_HOUR_RUN_LIST = [1, 2, 3, 4, 5]

TELE_BOT_TOKEN = os.getenv("TELE_BOT_TOKEN", "")
TELE_BOT_GROUP_ID = os.getenv("TELE_BOT_GROUP_ID", "")

ADB_HOST = os.getenv("ADB_HOST", "localhost")
ADB_PORT = int(os.getenv("ADB_PORT", 5037))


LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
LOGFORMAT = os.getenv("LOGFORMAT", "[%(asctime)s] [%(levelname)s] %(message)s")
LOG_FILE = os.getenv("LOG_FILE_PATH", "logs/app.log")
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 10))
