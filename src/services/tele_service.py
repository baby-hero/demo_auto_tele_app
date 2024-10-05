import time

from uiautomator2 import Device

from src.utils import notify_util
from src.utils.log_util import logger


class BaseTeleService:
    def __init__(self, device_ui: Device, serial_no: str):
        self.device_ui: Device = device_ui
        self.serial_no = serial_no
        self.package_name = "org.telegram.messenger"
        self.app_name = "Telegram"

    def _get_current_package_name(self) -> str:
        return self.device_ui.info.get("currentPackageName")

    def is_tele_home_screen(self) -> bool:
        return self.device_ui(
            description="Open navigation menu",
            clickable=True,
            packageName=self.package_name,
        ).exists(10)

    def _open_tele_app(self) -> bool:
        current_page = self._get_current_package_name()
        if current_page != self.package_name:
            self.device_ui.app_start(self.package_name)
            pid_app = self.device_ui.app_wait(self.package_name, front=True)
            if pid_app:
                logger.info(f"[{self.serial_no}] Open {self.app_name} successfully")
                return True
            else:
                logger.error(f"[{self.serial_no}] Open {self.app_name} failed")
                return False
        else:
            logger.info(f"[{self.serial_no}] {self.app_name} already opened")
            return True

    def close_tele_app(self) -> bool:
        current_page = self._get_current_package_name()
        if current_page == self.package_name:
            self.device_ui.press(
                "recent",
            )
            self.device_ui.swipe_ext("up", duration=0.015)
            logger.info(f"[{self.serial_no}] Close {self.app_name} successfully")
            self.device_ui.press("home")
            current_page = self._get_current_package_name()
        return current_page == self.package_name

    def back_to_app_home_screen(self) -> bool:
        count_back = 0
        while (
            not self.is_tele_home_screen()
            and self._get_current_package_name() == self.package_name
        ):
            count_back += 1
            logger.info(
                f"[{self.serial_no}] Press back to tele home...{count_back} times"
            )
            self.back_to_a_screen()

        if self._get_current_package_name() != self.package_name:
            logger.error(
                f"[{self.serial_no}] Back to tele home failed after {count_back} times"
            )
            self.close_tele_app()
            # try to open tele app again
            self._open_tele_app()

        result = self.is_tele_home_screen()
        if result:
            logger.info(f"[{self.serial_no}] Back to tele home successfully")
            return True
        else:
            logger.error(f"[{self.serial_no}] Back to tele home failed")
            raise ValueError(f"[{self.serial_no}] Back to tele home failed")

    def back_to_a_screen(self) -> bool:
        self.device_ui.press("back")
        return True

    def _notify_to_tele(self, msg):
        notify_util.send_telegram_log(msg)


class BaseTeleGroupService(BaseTeleService):
    def __init__(self, device_ui: Device, serial_no: str):
        super().__init__(device_ui, serial_no)
        self.group_name = "Telegram"
        self.bot_menu_timeout = 30

    def _open_bot_menu(self) -> bool:
        result = self.device_ui(description="Bot menu").click_exists(10)
        if result:
            logger.info(
                f"[{self.serial_no}] Open bot page {self.group_name} successfully"
            )
            # wait for loading finished
            self._waiting_bot_menu_loaded()
        else:
            logger.error(f"[{self.serial_no}] Open bot page {self.group_name} failed")
        return result

    def _is_group_home_screen(self) -> bool:
        return self.device_ui(
            text=self.group_name,
            packageName=self.package_name,
        ).exists(20)

    def _open_group_chat(self) -> bool:
        if not self.is_tele_home_screen():
            logger.info(f"[{self.serial_no}] Try switch to tele home screen")
            self.back_to_app_home_screen()

        """Open group chat from tele home screen"""
        group_index = self.get_group_index()
        btn_group_press = (
            self.device_ui(
                className="androidx.recyclerview.widget.RecyclerView",
                packageName=self.package_name,
            )
            .child(index=group_index)
            .click_exists(20)
        )
        if btn_group_press:
            logger.info(
                f"[{self.serial_no}] Open group: {self.group_name} successfully"
            )
        else:
            logger.error(f"[{self.serial_no}] Open group: {self.group_name} failed")
        return self._is_group_home_screen()

    def _close_bot_menu(self) -> bool:
        result = (
            self.device_ui(
                text=self.group_name,
                packageName=self.package_name,
            )
            .sibling(index=0)
            .click_exists(10)
        )
        if result:
            logger.info(
                f"[{self.serial_no}] Close bot page {self.group_name} successfully"
            )
        else:
            logger.error(f"[{self.serial_no}] Close bot page {self.group_name} failed")

        return result

    def start_group(self) -> bool:
        if not self._open_tele_app():
            logger.error(f"[{self.serial_no}] Open {self.app_name} failed")
            return False
        if not self._open_group_chat():
            logger.error(f"[{self.serial_no}] Open group {self.group_name} failed")
            return False
        if not self._open_bot_menu():
            logger.error(f"[{self.serial_no}] Open bot page {self.group_name} failed")
            return False

        return True

    def end_group(self) -> bool:
        """Back to Tele home screen"""
        if self._close_bot_menu():
            # BACK TO APP HOME SCREEN
            return self.back_to_a_screen()
        else:
            logger.error(f"[{self.serial_no}] Close bot page {self.group_name} failed")
            return False

    def _waiting_bot_menu_loaded(self) -> bool:
        logger.info(
            f"[{self.serial_no}] Waiting for bot menu loaded"
            f" in {self.bot_menu_timeout}s..."
        )
        time.sleep(self.bot_menu_timeout)

    def get_group_index(self) -> int:
        raise NotImplementedError(
            f"[{self.serial_no}] Subclasses must implement this method"
        )

    def run_app(self) -> bool:
        raise NotImplementedError(
            f"[{self.serial_no}] Subclasses must implement"
            f"this method on {self.group_name}"
        )
