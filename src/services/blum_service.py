import time

from uiautomator2 import Device

from src.services.tele_service import BaseTeleGroupService
from src.utils.log_util import logger


class BlumService(BaseTeleGroupService):
    def __init__(self, device_ui: Device, serial_no: str) -> None:
        super().__init__(device_ui, serial_no)
        self.group_name = "Blum"
        logger.info(f"[{self.serial_no}] Init {self.group_name} in {self.app_name}")

    def get_group_index(self) -> int:
        """Find group index in tele app start_index from 0"""
        return 1

    def run_app(self) -> bool:
        try:
            if not self.start_group():
                return False
            self._claim_daily_rewards()
            self._farming_rewards()
            return self.end_group()
        except Exception as e:
            logger.error(f"[{self.serial_no}] Error running app {self.app_name}:", e)
            return False

    def _waiting_bot_menu_loaded(self) -> bool:
        # TODO: CHANGE THIS CONDITION BECAUSE DAILY IS CLAIMED
        logger.info(f"[{self.serial_no}] Waiting for bot menu loaded")
        self.device_ui(
            text="Home",
            packageName=self.package_name,
        ).wait(timeout=self.bot_menu_timeout)
        return True

    def _claim_daily_rewards(self) -> bool:
        result = (
            self.device_ui(
                text="Your daily rewards",
                packageName=self.package_name,
            )
            .sibling(
                text="Continue",
                clickable=True,
            )
            .click_exists(10)
        )
        if result:
            logger.info(f"[{self.serial_no}] Claim daily rewards successfully")
        else:
            logger.error(f"[{self.serial_no}] claim daily rewards failed or claimed")
            return False
        return True

    def _farming_rewards(self) -> bool:
        claim_result = self.device_ui(
            textStartsWith="Claim ",
            clickable=True,
            packageName=self.package_name,
        ).click_exists(20)
        if claim_result:
            logger.info(f"[{self.serial_no}] Claim farming rewards successfully")
            time.sleep(10)

        start_farming_result = self.device_ui(
            text="Start farming",
            clickable=True,
            packageName=self.package_name,
        ).click_exists(20)
        if start_farming_result:
            logger.info(f"[{self.serial_no}] Start farming rewards successfully")
            time.sleep(10)

        return True
