import time

from uiautomator2 import Device

from src.services.tele_service import BaseTeleGroupService
from src.utils.log_util import logger


class SideFansService(BaseTeleGroupService):
    def __init__(self, device_ui: Device, serial_no: str) -> None:
        super().__init__(device_ui, serial_no)
        self.group_name = "SideFans (By SideKick)"
        logger.info(f"[{self.serial_no}] Init {self.group_name} in {self.app_name}")

    def get_group_index(self) -> int:
        """Find group index in tele app start_index from 0"""
        return 3

    def _close_bot_menu(self) -> bool:
        if super()._close_bot_menu():
            if self.device_ui(
                text="Close anyway", index=1, packageName=self.package_name
            ).click_exists(20):
                logger.info(
                    f"[{self.serial_no}] Close group: {self.group_name} successfully"
                )
                self.back_to_a_screen()
                return True
            else:
                logger.error(f"[{self.serial_no}] Not found 'Close anyway' button")
        logger.error(f"[{self.serial_no}] Close group: {self.group_name} failed")
        return False

    def run_app(self) -> bool:
        try:
            if not self.start_group():
                return False
            # TODO: check loading status
            time.sleep(15)

            self.daily_check_in()
            return self.end_group()
        except Exception as e:
            logger.error(f"[{self.serial_no}] Error running app {self.app_name}:", e)
            return False

    def daily_check_in(self) -> bool:
        logger.info(f"[{self.serial_no}] Daily check-in started...")
        if not self._switch_tap_pass():
            return False

        if not self._press_go_btn():
            return False

        if not self.device_ui(
            text="Claim",
            index=4,
            clickable="true",
            packageName=self.package_name,
        ).click_exists(10):
            logger.error(
                f"[{self.serial_no}] Claim button not found, maybe claimed already"
            )
            return False
        else:
            logger.info(f"[{self.serial_no}] Daily check-in successfully")
        time.sleep(5)
        close_btn_press = (
            self.device_ui(
                text="Daily check-in",
                index=0,
                packageName=self.package_name,
            )
            .sibling(index=1)
            .click_exists(10)
        )
        if not close_btn_press:
            logger.error(f"[{self.serial_no}] Close button not found")
            self.back_to_a_screen()
            logger.error(f"[{self.serial_no}] Try to back to a screen")
            return False
        return True

    def _switch_tap_pass(self) -> bool:
        result = self.device_ui(
            description="Pass", packageName=self.package_name
        ).click_exists(20)
        if result:
            logger.info(f"[{self.serial_no}] Tap pass successfully")
        else:
            logger.error(f"[{self.serial_no}] Tap pass failed")
        return result

    def _press_go_btn(self, index: int = 3, instance: int = 0) -> bool:
        result = self.device_ui(
            text="GO",
            index=3,
            instance=instance,
            packageName=self.package_name,
        ).click_exists(10)
        if result:
            logger.info(f"[{self.serial_no}] Press GO successfully")
        else:
            logger.error(f"[{self.serial_no}] Press GO failed")
        return result
