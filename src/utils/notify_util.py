import threading

import requests

from src.configs.common_config import TELE_BOT_GROUP_ID, TELE_BOT_TOKEN
from src.utils.log_util import logger


def send_message(msg):
    try:
        logger.warning(f"Send Telegram log: {msg}")
        if TELE_BOT_TOKEN and TELE_BOT_GROUP_ID:
            response = requests.get(
                f"https://api.telegram.org/bot{TELE_BOT_TOKEN}/"
                f"sendMessage?chat_id={TELE_BOT_GROUP_ID}&text={msg[:1000]}"
            )
            response.raise_for_status()
            logger.warning(f"FINISH Send Telegram log: {msg}")
    except Exception as e:
        logger.error(f"TelegramLog error: {e}")


def send_telegram_log(message):
    threading.Thread(target=send_message, args=(message,)).start()


if __name__ == "__main__":
    send_telegram_log("Test Telegram log")
