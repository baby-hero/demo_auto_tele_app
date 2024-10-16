import time
from datetime import datetime

from uiautomator2 import Device

from model.config_device import ConfigDevice
from src.configs.common_config import UI_TIMEOUT
from src.services.tele_service import BaseTeleGroupService
from src.utils import adb_util, common_util
from src.utils.log_util import logger


class BnbMoonBixService(BaseTeleGroupService):
    def __init__(
        self,
        device_ui: Device,
        serial_no: str,
        device_size,
        config_device: ConfigDevice,
    ) -> None:
        super().__init__(device_ui, serial_no, config_device)
        self.device_size = device_size
        self.group_name = "Binance Moonbix bot"
        self.waiting_next_run_interval = config_device.bnb_moonbix_delay_interval
        self.group_index = config_device.bnb_moonbix_group_id
        logger.info(f"[{self.device_name}] Init {self.group_name} in {self.app_name}")

    def _waiting_bot_menu_loaded(self) -> bool:
        logger.info(f"[{self.device_name}] Waiting for bot menu loaded")
        self.device_ui(
            text="Leaderboard",
            packageName=self.package_name,
        ).wait(timeout=self.bot_menu_timeout)
        return True

    def daily_check_in(self) -> bool:
        logger.info(f"[{self.device_name}] Daily check-in started...")
        node = self.device_ui(text="Your Daily Record", packageName=self.package_name)
        if node.exists(UI_TIMEOUT):
            result = node.sibling(text="Continue").click_exists(UI_TIMEOUT // 2)
            if result:
                logger.info(f"[{self.device_name}] Daily check-in successfully")
            else:
                logger.error(f"[{self.device_name}] Daily check-in failed")
            return result
        return True

    def run_app(self) -> bool:
        try:
            if not self._check_run_app():
                logger.info(
                    f"[{self.device_name}] Ignore running app {self.group_name}"
                )
                return False
            if not self.start_group():
                return False
            self.daily_check_in()

            self.run_game_on_device()

            self._set_run_last_at()
            return self.end_group()
        except Exception as e:
            logger.error(f"[{self.device_name}] Error running app {self.app_name}:", e)
            return False

    def _take_screenshot_to_check(self):
        try:
            time_ts = int(datetime.now().timestamp())
            node = (
                self.device_ui(
                    text="Security Verification",
                    packageName=self.package_name,
                )
                .sibling(index=2)
                .child(index=0)
            )
            img = node.screenshot()
            img.save(f"images/image_{time_ts}.png")

            img = node.child(index=0).screenshot()
            img.save(f"images/compare_{time_ts}.png")
        except Exception as e:
            logger.error(f"[{self.device_name}] Take screenshot failed", e)

    def _auto_click_to_play(
        self,
        play_round_time_s: int = 45,
        waiting_start_game: int = 25,
    ):
        result = self.device_ui(
            text="icon-timer",
            packageName=self.package_name,
        ).wait(timeout=waiting_start_game)
        if not result:
            logger.error(f"[{self.device_name}] Wait for start game failed")
            self._notify_to_tele(
                f"[{self.device_name}] Wait for start game failed, Maybe have error"
            )
            if not self.device_ui(
                text="icon-timer",
                packageName=self.package_name,
            ).wait(timeout=waiting_start_game * 3):
                logger.error(f"[{self.device_name}] Wait for start game failed")
                self.close_tele_app()
                return False

        logger.info(f"[{self.device_name}] Starting click in game...")

        start_ts = datetime.now()
        count = 0

        while True:
            click_position = adb_util.get_random_position_to_click(self.device_size)
            self.device_ui.click(*click_position)
            if count % 20 == 0:
                logger.info(f"[{self.device_name}] Clicked at {click_position}")
            count += 1
            time.sleep(common_util.random_float_in_range())
            if (datetime.now() - start_ts).seconds > play_round_time_s:
                time.sleep(3)
                break
        logger.info(f"[{self.device_name}] Game ended: clicked {count} times.")

    def _check_and_click_by_btn_name(
        self, btn_text: str, btn_index: int = None
    ) -> bool:
        if btn_index:
            node = self.device_ui(
                textStartsWith=btn_text,
                clickable=True,
                enabled=True,
                packageName=self.package_name,
            )
        else:
            node = self.device_ui(
                textStartsWith=btn_text,
                clickable=True,
                enabled=True,
                packageName=self.package_name,
            )
        if node.exists(UI_TIMEOUT):
            node_text = node.get_text()
            logger.info(f"[{self.device_name}] Clicking on button: {node_text}")
            return node.click_exists(UI_TIMEOUT // 2)
        logger.info(f"[{self.device_name}] Not Found node for text '{btn_text}'")
        return False

    def _get_balance(self) -> int:
        try:
            node = self.device_ui(text="Available points")
            if node.exists(UI_TIMEOUT // 2):
                txt_balance = self.device_ui(text="Available points").sibling(index=2)
                balance_text = txt_balance.get_text()
                logger.info(f"[{self.device_name}] Balance: {balance_text}")
                return int(balance_text.replace(",", ""))
            else:
                logger.error(
                    f"[{self.device_name}] Not Found node for text 'Available points'"
                )
        except Exception as e:
            logger.error(f"[{self.device_name}] Error getting balance,", e)
        return -1

    def run_game_on_device(self):
        logger.info(f"[{self.device_name}] Run game")
        self.device_to_balance_dict: dict = {}
        played_flag = False
        retry = 3
        count = 0
        while True:
            is_running_game_flag = False
            count += 1
            if self._check_and_click_by_btn_name(
                "Play Game",
            ):
                is_running_game_flag = True
                self._auto_click_to_play()

                while self._check_and_click_by_btn_name(
                    "Play Again (🚀 Left",
                ):
                    self._auto_click_to_play()

                self._check_and_click_by_btn_name(
                    "Continue",
                )

            if not is_running_game_flag:
                acc_balance = self._get_balance()
                if acc_balance > 0:
                    self.device_to_balance_dict[self.device_name] = acc_balance
                break
            else:
                played_flag = True
            if count > retry:
                self._notify_to_tele(
                    f"[{self.device_name}] Play game retry 3 times. Stopping"
                )
                break
        logger.info(f"[{self.device_name}] Finished game: {played_flag} flag")
        return played_flag
