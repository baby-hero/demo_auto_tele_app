import requests

from src.configs import TELE_BOT_GROUP_ID, TELE_BOT_TOKEN
from src.utils.log_util import logger


def send_telegram_log(message):
    try:
        if TELE_BOT_TOKEN and TELE_BOT_GROUP_ID:
            requests.get(
                f"https://api.telegram.org/bot{TELE_BOT_TOKEN}/"
                f"sendMessage?chat_id={TELE_BOT_GROUP_ID}&text={message[:1000]}"
            )
    except Exception as e:
        logger.error(f"TelegramLog error: {e}")
