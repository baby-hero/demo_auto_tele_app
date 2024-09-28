import time
from datetime import datetime

from uiautomator2 import Device

from src.services.tele_service import BaseTeleGroupService
from src.utils import adb_util, common_util
from src.utils.log_util import logger


class BnbMoonBixService(BaseTeleGroupService):
    def __init__(self, device_ui: Device, serial_no: str, device_size) -> None:
        super().__init__(device_ui, serial_no)
        self.device_size = device_size
        self.group_name = "Binance Moonbix bot"
        self.group_index = 1
        logger.info(f"[{self.serial_no}] Init {self.group_name} in {self.app_name}")

    def get_group_index(self) -> int:
        """Find group index in tele app start_index from 0"""
        return 0

    def daily_check_in(self) -> bool:
        logger.info(f"[{self.serial_no}] Daily check-in started...")
        node = self.device_ui(text="Your Daily Record", packageName=self.package_name)
        if node.exists(20):
            result = node.sibling(text="Continue").click_exists(10)
            if result:
                logger.info(f"[{self.serial_no}] Daily check-in successfully")
            else:
                logger.error(f"[{self.serial_no}] Daily check-in failed")
            return result
        return True

    def run_app(self, device_to_balance_dict: dict) -> bool:
        try:
            if not self.start_group():
                return False
            self.daily_check_in()

            self.run_game_on_device(device_to_balance_dict)

            return self.end_group()
        except Exception as e:
            logger.error(f"[{self.serial_no}] Error running app {self.app_name}:", e)
            return False

    def _auto_click_to_play(
        self,
        play_round_time_s: int = 50,
        waiting_start_game: int = 3,
    ):
        time.sleep(waiting_start_game)
        logger.info(f"[{self.serial_no}] Starting click in game...")
        start_ts = datetime.now()
        count = 0

        while True:
            click_position = adb_util.get_random_position_to_click(self.device_size)
            self.device_ui.click(*click_position)
            if count % 20 == 0:
                logger.info(f"[{self.serial_no}] Clicked at {click_position}")
            count += 1
            time.sleep(common_util.random_float_in_range())
            if (datetime.now() - start_ts).seconds > play_round_time_s:
                break
        logger.info(f"[{self.serial_no}] Game ended: clicked {count} times.")

    def _check_and_click_by_btn_name(
        self, btn_text: str, btn_index: int = None
    ) -> bool:
        if btn_index:
            node = self.device_ui(
                textStartsWith=btn_text,
                index=btn_index,
                clickable=True,
                packageName=self.package_name,
            )
        else:
            node = self.device_ui(
                textStartsWith=btn_text, clickable=True, packageName=self.package_name
            )
        if node.exists(20):
            node_text = node.get_text()
            logger.info(f"[{self.serial_no}] Clicking on button: {node_text}")
            return node.click_exists(10)
        logger.info(f"[{self.serial_no}] Not Found node for text '{btn_text}'")
        return False

    def _get_balance(self) -> int:
        try:
            node = self.device_ui(text="Available points")
            if node.exists(10):
                txt_balance = self.device_ui(text="Available points").sibling(index=2)
                balance_text = txt_balance.get_text()
                logger.info(f"[{self.serial_no}] Balance: {balance_text}")
                return int(balance_text.replace(",", ""))
            else:
                logger.error(
                    f"[{self.serial_no}] Not Found node for text 'Available points'"
                )
        except Exception as e:
            logger.error(f"[{self.serial_no}] Error getting balance,", e)
        return -1

    def run_game_on_device(self, device_to_balance_dict: dict):
        logger.info(f"[{self.serial_no}] Run game")
        self.device_to_balance_dict: dict = device_to_balance_dict
        played_flag = False
        while True:
            is_running_game_flag = False

            if self._check_and_click_by_btn_name(
                "Play Game",
            ):
                is_running_game_flag = True
                self._auto_click_to_play()
            else:
                while self._check_and_click_by_btn_name(
                    "Play Again (🚀 Left",
                ):
                    is_running_game_flag = True
                    self._auto_click_to_play()
                self._check_and_click_by_btn_name(
                    "Continue",
                )

            if not is_running_game_flag:
                acc_balance = self._get_balance()
                if acc_balance > 0:
                    self.device_to_balance_dict[self.serial_no] = acc_balance
                break
            else:
                played_flag = True
        logger.info(f"[{self.serial_no}] Finished game: {played_flag} flag")
        return played_flag
