import time

from uiautomator2 import Device

from src.services.tele_service import BaseTeleGroupService
from src.utils.log_util import logger


class SideFansService(BaseTeleGroupService):
    def __init__(
        self, device_ui: Device, serial_no: str, general_configs: dict
    ) -> None:
        super().__init__(device_ui, serial_no, general_configs)
        self.group_name = "SideFans (By SideKick)"
        self.waiting_next_run_interval = 12 * 60 * 60
        logger.info(f"[{self.serial_no}] Init {self.group_name} in {self.app_name}")

    def get_group_index(self) -> int:
        """Find group index in tele app start_index from 0"""
        return 3

    def _waiting_bot_menu_loaded(self) -> bool:
        logger.info(f"[{self.serial_no}] Waiting for bot menu loaded")
        self.device_ui(
            text="Rewards",
            packageName=self.package_name,
        ).wait(timeout=self.bot_menu_timeout)
        return True

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
            if not self._check_run_app():
                logger.info(f"[{self.serial_no}] Ignore running app {self.group_name}")
                return False
            if not self.start_group():
                return False
            # TODO: check loading status
            time.sleep(15)
            if not self._handle_pass_tap():
                logger.error(f"[{self.serial_no}] handle pass tap failed")
                return False
            else:
                logger.info(f"[{self.serial_no}] handle pass tap successfully")
            self._set_pre_run_at()
            return self.end_group()
        except Exception as e:
            logger.error(f"[{self.serial_no}] Error running app {self.app_name}:", e)
            return False

    def _handle_pass_tap(self) -> bool:
        if not self._switch_tap_pass():
            return False
        self._daily_check_in()

        # Handle Other tasks
        while True:
            if not self.handle_btn_go_in_pass_tap():
                break
        return True

    def _daily_check_in(self) -> bool:
        logger.info(f"[{self.serial_no}] Daily check-in started...")
        result = self.device_ui(
            text="GO",
            packageName=self.package_name,
        ).click_exists(20)
        if result:
            logger.info(f"[{self.serial_no}] Press GO successfully")
        else:
            logger.error(f"[{self.serial_no}] Press GO failed")
            return False
        # scroll to end of daily check
        time.sleep(3)
        self.device_ui(scrollable=True).scroll(action="toEnd", steps=25)
        daily_flag = True

        if not self.device_ui(
            text="Claim",
            index=4,
            clickable=True,
            packageName=self.package_name,
        ).click_exists(10):
            logger.error(
                f"[{self.serial_no}] Claim button not found, maybe claimed already"
            )
            daily_flag = False
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
        return daily_flag

    def _switch_tap_pass(self) -> bool:
        result = self.device_ui(
            description="Pass", packageName=self.package_name
        ).click_exists(20)
        if result:
            logger.info(f"[{self.serial_no}] Tap pass successfully")
        else:
            logger.error(f"[{self.serial_no}] Tap pass failed")
        return result

    def handle_btn_go_in_pass_tap(self) -> bool:
        btn_go = self.device_ui(
            text="GO",
            packageName=self.package_name,
            instance=1,
        )
        if not btn_go.exists(10):
            return False
        task_name = btn_go.sibling(className="android.widget.TextView").get_text()
        if not btn_go.click_exists(10):
            logger.error(f"[{self.serial_no}] Press GO failed for task: {task_name}")
            return False
        else:
            logger.info(
                f"[{self.serial_no}] Press GO successfully for task: {task_name}"
            )
            time.sleep(3)
            self.back_to_a_screen()
            self.device_ui(description="Web tabs SideFans (By SideKick)").click_exists(
                10
            )
            return True
