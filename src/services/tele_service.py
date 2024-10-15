import time
from typing import List, Tuple

import cv2
import numpy as np
from uiautomator2 import Device

from src.configs.common_config import IMAGE_FOLDER_PATH, UI_TIMEOUT
from src.model.config_device import ConfigDevice
from src.utils import notify_util
from src.utils.log_util import logger


class BaseTeleService:
    def __init__(self, device_ui: Device, device_name: str):
        self.device_ui: Device = device_ui
        self.device_name = device_name
        self.package_name = "org.telegram.messenger"
        self.app_name = "Telegram"

    def _get_current_package_name(self) -> str:
        return self.device_ui.info.get("currentPackageName")

    def is_tele_home_screen(self) -> bool:
        return self.device_ui(
            description="Open navigation menu",
            clickable=True,
            packageName=self.package_name,
        ).exists(UI_TIMEOUT // 2)

    def _open_tele_app(self) -> bool:
        current_page = self._get_current_package_name()
        if current_page != self.package_name:
            self.device_ui.app_start(self.package_name)
            pid_app = self.device_ui.app_wait(self.package_name, front=True)
            if pid_app:
                logger.info(f"[{self.device_name}] Open {self.app_name} successfully")
                return True
            else:
                logger.error(f"[{self.device_name}] Open {self.app_name} failed")
                return False
        else:
            logger.info(f"[{self.device_name}] {self.app_name} already opened")
            return True

    def close_tele_app(self) -> bool:
        current_page = self._get_current_package_name()
        if current_page == self.package_name:
            self.device_ui.press(
                "recent",
            )
            self.device_ui.swipe_ext("up", duration=0.025)
            logger.info(f"[{self.device_name}] Close {self.app_name} successfully")
            self.device_ui.press("home")
            current_page = self._get_current_package_name()
        return current_page != self.package_name

    def back_to_app_home_screen(self) -> bool:
        count_back = 0
        while (
            not self.is_tele_home_screen()
            and self._get_current_package_name() == self.package_name
        ):
            count_back += 1
            logger.info(
                f"[{self.device_name}] Press back to tele home...{count_back} times"
            )
            self.back_to_a_screen()

        if self._get_current_package_name() != self.package_name:
            logger.error(
                f"[{self.device_name}] Back to tele home failed "
                f"after {count_back} times"
            )
            self.close_tele_app()
            # try to open tele app again
            self._open_tele_app()

        result = self.is_tele_home_screen()
        if result:
            logger.info(f"[{self.device_name}] Back to tele home successfully")
            return True
        else:
            logger.error(f"[{self.device_name}] Back to tele home failed")
            raise ValueError(f"[{self.device_name}] Back to tele home failed")

    def back_to_a_screen(self) -> bool:
        self.device_ui.press("back")
        return True

    def take_screenshot(self, item_screen=None, file_name="tmp.png") -> str:
        full_path = IMAGE_FOLDER_PATH + file_name
        if not item_screen:
            self.device_ui.screenshot(full_path)
        else:
            item_screen.screenshot(full_path)

        logger.info(f"[{self.device_name}] taken screenshot successfully")
        return full_path

    def _notify_to_tele(self, msg):
        notify_util.send_telegram_log(msg)


class BaseTeleGroupService(BaseTeleService):
    def __init__(
        self, device_ui: Device, device_name: str, config_device: ConfigDevice
    ):
        super().__init__(device_ui, device_name)
        self.group_name = "Telegram"
        self.bot_menu_timeout = 30
        self.waiting_next_run_interval: int = 3600
        self.config_device: ConfigDevice = config_device
        self.group_index = -1

    def _get_run_last_at(self) -> int:
        return self.config_device.last_running_ts_by_group_id.get(
            self.get_group_index(), 0
        )

    def _set_run_last_at(self) -> bool:
        current_time = int(time.time())
        self.config_device.last_running_ts_by_group_id[
            self.get_group_index()
        ] = current_time
        return True

    def _check_run_app(self) -> bool:
        current_time = int(time.time())
        pre_run_at = self._get_run_last_at()
        return (current_time - pre_run_at) >= self.waiting_next_run_interval

    def _open_bot_menu(self) -> bool:
        result = self.device_ui(description="Bot menu").click_exists(UI_TIMEOUT // 2)
        if result:
            logger.info(
                f"[{self.device_name}] Open bot page {self.group_name} successfully"
            )
            self.device_ui(
                text="Start",
                clickable=True,
                packageName=self.package_name,
            ).click_exists(UI_TIMEOUT // 2)
            # wait for loading finished
            self._waiting_bot_menu_loaded()
        else:
            logger.error(f"[{self.device_name}] Open bot page {self.group_name} failed")
        return result

    def _is_group_home_screen(self) -> bool:
        return self.device_ui(
            text=self.group_name,
            packageName=self.package_name,
        ).exists(UI_TIMEOUT)

    def _open_group_chat(self) -> bool:
        if not self.is_tele_home_screen():
            logger.info(f"[{self.device_name}] Try switch to tele home screen")
            self.back_to_app_home_screen()

        """Open group chat from tele home screen"""
        group_index = self.get_group_index()
        btn_group_press = (
            self.device_ui(
                className="androidx.recyclerview.widget.RecyclerView",
                packageName=self.package_name,
            )
            .child(index=group_index)
            .click_exists(UI_TIMEOUT)
        )
        if btn_group_press:
            logger.info(
                f"[{self.device_name}] Open group: {self.group_name} successfully"
            )
        else:
            logger.error(f"[{self.device_name}] Open group: {self.group_name} failed")
        return self._is_group_home_screen()

    def _close_bot_menu(self) -> bool:
        result = (
            self.device_ui(
                text=self.group_name,
                packageName=self.package_name,
            )
            .sibling(index=0)
            .click_exists(UI_TIMEOUT // 2)
        )
        if result:
            logger.info(
                f"[{self.device_name}] Close bot page {self.group_name} successfully"
            )
        else:
            logger.error(
                f"[{self.device_name}] Close bot page {self.group_name} failed"
            )

        return result

    def start_group(self) -> bool:
        if not self._open_tele_app():
            logger.error(f"[{self.device_name}] Open {self.app_name} failed")
            return False
        if not self._open_group_chat():
            logger.error(f"[{self.device_name}] Open group {self.group_name} failed")
            return False
        if not self._open_bot_menu():
            logger.error(f"[{self.device_name}] Open bot page {self.group_name} failed")
            return False

        return True

    def end_group(self) -> bool:
        """Back to Tele home screen"""
        if self._close_bot_menu():
            # BACK TO APP HOME SCREEN
            return self.back_to_a_screen()
        else:
            logger.error(
                f"[{self.device_name}] Close bot page {self.group_name} failed"
            )
            return False

    def _waiting_bot_menu_loaded(self) -> bool:
        logger.info(
            f"[{self.device_name}] Waiting for bot menu loaded"
            f" in {self.bot_menu_timeout}s..."
        )
        time.sleep(self.bot_menu_timeout)
        return True

    def get_group_index(self) -> int:
        if self.group_index >= 0:
            return self.group_index

        raise NotImplementedError(
            f"[{self.device_name}] Subclasses must implement this method"
        )

    def find_items(
        self,
        item_path="",
        threshold=0.95,
        num_div: int = 3,
        add_x=0,
        add_y=0,
    ) -> List[Tuple[int, int]]:
        item_template = cv2.imread(item_path)
        screenshot = self.device_ui.screenshot(format="opencv")
        # gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        # gray_item_template = cv2.cvtColor(item_template, cv2.COLOR_BGR2HSV)
        result = cv2.matchTemplate(
            screenshot, item_template, cv2.TM_CCOEFF_NORMED
        )
        loc = np.where(result >= threshold)
        (height, width, _) = item_template.shape
        i = width // num_div
        j = height // num_div
        int_tuples = {
            ((int(x) // i + add_x) * i, (int(y) // j + add_y) * j)
            for x, y in list(zip(*loc[::-1]))
        }
        for (x, y) in int_tuples:
            cv2.rectangle(
                screenshot,
                (x, y),
                (x + item_template.shape[1], y + item_template.shape[0]),
                (255, 0, 0),
                2,
            )
        cv2.imwrite(
            f"resources/image/tmp/matched_{self.device_name}_{self.group_index}.png",
            screenshot,
        )

        return list(int_tuples)

    def run_app(self) -> bool:
        raise NotImplementedError(
            f"[{self.device_name}] Subclasses must implement"
            f"this method on {self.group_name}"
        )
