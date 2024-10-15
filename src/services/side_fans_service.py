import time

from uiautomator2 import Device

from model.config_device import ConfigDevice
from src.configs import side_fans_config
from src.configs.common_config import UI_TIMEOUT
from src.services.tele_service import BaseTeleGroupService
from src.utils.log_util import logger


class SideFansService(BaseTeleGroupService):
    def __init__(
        self, device_ui: Device, serial_no: str, config_device: ConfigDevice
    ) -> None:
        super().__init__(device_ui, serial_no, config_device)
        self.group_name = "SideFans (By SideKick)"
        self.waiting_next_run_interval = config_device.side_fans_delay_interval
        self.group_index = config_device.side_fans_group_id
        logger.info(f"[{self.device_name}] Init {self.group_name} in {self.app_name}")

    def _waiting_bot_menu_loaded(self) -> bool:
        logger.info(f"[{self.device_name}] Waiting for bot menu loaded")
        self.device_ui(
            text="Rewards",
            packageName=self.package_name,
        ).wait(timeout=self.bot_menu_timeout)
        return True

    def _close_bot_menu(self) -> bool:
        if super()._close_bot_menu():
            if self.device_ui(
                text="Close anyway", index=1, packageName=self.package_name
            ).click_exists(UI_TIMEOUT):
                logger.info(
                    f"[{self.device_name}] Close group: {self.group_name} successfully"
                )
                self.back_to_a_screen()
                return True
            else:
                logger.error(f"[{self.device_name}] Not found 'Close anyway' button")
        logger.error(f"[{self.device_name}] Close group: {self.group_name} failed")
        return False

    def run_app(self) -> bool:
        try:
            if not self._check_run_app():
                logger.info(
                    f"[{self.device_name}] Ignore running app {self.group_name}"
                )
                return False
            if not self.start_group():
                return False
            if not self._handle_pass_tap():
                logger.error(f"[{self.device_name}] handle pass tap failed")
                return False
            else:
                logger.info(f"[{self.device_name}] handle pass tap successfully")

            if not self._handle_rewards_tap():
                logger.error(f"[{self.device_name}] handle rewards tap failed")
                return False
            else:
                logger.info(f"[{self.device_name}] handle rewards tap successfully")

            self._set_run_last_at()
            return self.end_group()
        except Exception as e:
            logger.error(f"[{self.device_name}] Error running app {self.app_name}", e)
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

    def _handle_rewards_tap(self) -> bool:
        if not self._switch_rewards_tap():
            return False
        # Handle Other tasks
        time.sleep(3)
        self._handle_btn_tasks_in_rewards_tap()
        # close tasks tap
        self.device_ui(
            text="Tasks",
            instance=2,
            packageName=self.package_name,
        ).sibling(className="android.widget.Image", clickable=True,).click_exists(
            UI_TIMEOUT // 2
        )
        return True

    def _handle_btn_tasks_in_rewards_tap(self):
        result = self.device_ui(
            text="Tasks", clickable=True, enabled=True, packageName=self.package_name
        ).click_exists(UI_TIMEOUT)
        if not result:
            logger.error(f"[{self.device_name}] Tasks button not found")
            return False
        logger.info(f"[{self.device_name}] Click Tasks successfully")
        self.device_ui(text="Tasks", instance=2, packageName=self.package_name).wait(
            timeout=UI_TIMEOUT
        )
        self._find_and_check_tasks_in_rewards_tap()
        return True

    def _find_and_check_tasks_in_rewards_tap(self):
        logger.info(f"[{self.device_name}] Start check tasks in rewards tap")
        self._find_and_check_tasks_by_pages_in_rewards_tab(page_index=0)

        scrollable_view = self.device_ui(scrollable=True, packageName=self.package_name)
        if not scrollable_view:
            logger.error(f"[{self.device_name}] Scrollable not found")
            return True
        page_index = 1
        pre_text_of_first_task = self._get_text_of_first_task_in_rewards_tab()
        while True:
            # scroll down to load more tasks
            scrollable_view.scroll(direction="down", step=20)
            text_of_first_task_in_page = self._get_text_of_first_task_in_rewards_tab()
            if (
                text_of_first_task_in_page
                and pre_text_of_first_task == text_of_first_task_in_page
            ):
                logger.info(f"[{self.device_name}] No new tasks in page: {page_index}")
                break
            pre_text_of_first_task = text_of_first_task_in_page
            logger.info(
                f"[{self.device_name}] Page {page_index} loaded, "
                f" with first task: {text_of_first_task_in_page}"
            )
            self._find_and_check_tasks_by_pages_in_rewards_tab(page_index=page_index)
            page_index = page_index + 1

        return True

    def _get_text_of_first_task_in_rewards_tab(self):
        try:
            return (
                self.device_ui(text="Tasks", instance=2, packageName=self.package_name)
                .sibling(
                    scrollable=True,
                )
                .child(className="android.widget.Button")
                .get_text(timeout=UI_TIMEOUT)
            )
        except Exception as e:
            logger.error(
                f"[{self.device_name}] Error get text of first task in rewards tab", e
            )
        return ""

    def _find_and_check_tasks_by_pages_in_rewards_tab(self, page_index: int):
        logger.info(
            f"[{self.device_name}] Start check tasks by pages in rewards tap,"
            f" page: {page_index}"
        )
        uncheck_btn_path = side_fans_config.UNCHECK_ITEM_PATH
        uncheck_btn_list = self.find_items(uncheck_btn_path, threshold=0.9)
        if not uncheck_btn_list:
            logger.error(
                f"[{self.device_name}] Uncheck button not found in page: {page_index}"
            )
            return True

        if page_index == 0:
            # ignore invite 5 friends button
            uncheck_btn_list.sort()
            uncheck_btn_list = uncheck_btn_list[1:]
        logger.info(
            f"[{self.device_name}] found {len(uncheck_btn_list)} uncheck task "
            f"in page: {page_index}"
        )
        for i, (x, y) in enumerate(uncheck_btn_list):
            if self.device_ui(
                text="Tasks", instance=2, packageName=self.package_name
            ).exists(UI_TIMEOUT // 2):
                logger.info(
                    f"[{self.device_name}] Clicking task {i} in page {page_index}"
                )
                self.device_ui.click(x, y)
                time.sleep(UI_TIMEOUT // 2)
                if self._get_current_package_name() != self.package_name:
                    # Case: open other app
                    logger.info(
                        f"[{self.device_name}] Back task {i} from other app "
                        f"in page {page_index}"
                    )
                    self.device_ui.press("recent")
                    self.device_ui.swipe_ext("up", duration=0.025)
                    self.device_ui.press("recent")
                else:
                    logger.info(
                        f"[{self.device_name}] Back task {i} in page {page_index}"
                    )
                    self.back_to_a_screen()
                    self._open_web_tabs_side_fans()
        return True

    def _daily_check_in(self) -> bool:
        logger.info(f"[{self.device_name}] Daily check-in started...")
        result = self.device_ui(
            text="GO",
            packageName=self.package_name,
        ).click_exists(UI_TIMEOUT)
        if result:
            logger.info(f"[{self.device_name}] Press GO successfully")
        else:
            logger.error(f"[{self.device_name}] Press GO failed")
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
        ).click_exists(UI_TIMEOUT // 2):
            logger.error(
                f"[{self.device_name}] Claim button not found, maybe claimed already"
            )
            daily_flag = False
        else:
            logger.info(f"[{self.device_name}] Daily check-in successfully")
        time.sleep(5)
        close_btn_press = (
            self.device_ui(
                text="Daily check-in",
                index=0,
                packageName=self.package_name,
            )
            .sibling(index=1)
            .click_exists(UI_TIMEOUT // 2)
        )
        if not close_btn_press:
            logger.error(f"[{self.device_name}] Close button not found")
            self.back_to_a_screen()
            logger.error(f"[{self.device_name}] Try to back to a screen")
            return False
        return daily_flag

    def _switch_rewards_tap(self) -> bool:
        result = self.device_ui(
            description="Rewards", packageName=self.package_name
        ).click_exists(UI_TIMEOUT)
        if result:
            logger.info(f"[{self.device_name}] Rewards Tap successfully")
        else:
            logger.error(f"[{self.device_name}] Rewards Tap failed")
        return result

    def _switch_tap_pass(self) -> bool:
        result = self.device_ui(
            description="Pass", packageName=self.package_name
        ).click_exists(UI_TIMEOUT)
        if result:
            logger.info(f"[{self.device_name}] Tap pass successfully")
        else:
            logger.error(f"[{self.device_name}] Tap pass failed")
        return result

    def handle_btn_go_in_pass_tap(self) -> bool:
        btn_go = self.device_ui(
            text="GO",
            packageName=self.package_name,
            instance=1,
        )
        if not btn_go.exists(UI_TIMEOUT // 2):
            return False
        task_name = btn_go.sibling(className="android.widget.TextView").get_text()
        if not btn_go.click_exists(UI_TIMEOUT // 2):
            logger.error(f"[{self.device_name}] Press GO failed for task: {task_name}")
            return False
        else:
            logger.info(
                f"[{self.device_name}] Press GO successfully for task: {task_name}"
            )
            time.sleep(3)
            self.back_to_a_screen()
            self._open_web_tabs_side_fans()
            return True

    def _open_web_tabs_side_fans(self):
        self.device_ui(description="Web tabs SideFans (By SideKick)").click_exists(10)
