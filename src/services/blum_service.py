import time
from typing import Literal

from uiautomator2 import Device

from model.config_device import ConfigDevice
from src.configs.blum_config import (
    TASK_TO_VERIFY_DICT,
    START_ITEM_PATH,
    START_WEEKLY_ITEM_PATH,
    CLAIM_ITEM_PATH,
    KEYWORD_ITEM_PATH,
    VERIFY_ITEM_PATH,
)
from src.configs.common_config import UI_TIMEOUT
from src.services.tele_service import BaseTeleGroupService
from src.utils.log_util import logger


class BlumService(BaseTeleGroupService):
    def __init__(
        self, device_ui: Device, serial_no: str, config_device: ConfigDevice
    ) -> None:
        super().__init__(device_ui, serial_no, config_device)
        self.group_name = "Blum"
        self.waiting_next_run_interval = config_device.blum_delay_interval
        self.group_index = config_device.blum_group_id
        logger.info(f"[{self.device_name}] Init {self.group_name} in {self.app_name}")

    def run_app(self) -> bool:
        try:
            if not self._check_run_app():
                logger.info(
                    f"[{self.device_name}] Ignore running app {self.group_name}"
                )
                return False
            if not self.start_group():
                return False
            self._claim_daily_rewards()
            self._farming_rewards()
            self._handle_earn()
            self._set_run_last_at()
            return self.end_group()
        except Exception as e:
            logger.error(f"[{self.device_name}] Error running app {self.app_name}:", e)
            return False

    def _waiting_bot_menu_loaded(self) -> bool:
        logger.info(f"[{self.device_name}] Waiting for bot menu loaded")
        self.device_ui(
            description="Home",
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
            .click_exists(UI_TIMEOUT // 2)
        )
        if result:
            logger.info(f"[{self.device_name}] Claim daily rewards successfully")
        else:
            logger.error(f"[{self.device_name}] claim daily rewards failed or claimed")
            return False
        return True

    def _farming_rewards(self) -> bool:
        claim_result = self.device_ui(
            textStartsWith="Claim ",
            clickable=True,
            packageName=self.package_name,
        ).click_exists(UI_TIMEOUT)
        if claim_result:
            logger.info(f"[{self.device_name}] Claim farming rewards successfully")
            time.sleep(10)

        start_farming_result = self.device_ui(
            text="Start farming",
            clickable=True,
            packageName=self.package_name,
        ).click_exists(UI_TIMEOUT)
        if start_farming_result:
            logger.info(f"[{self.device_name}] Start farming rewards successfully")
            time.sleep(10)

        return True

    def _handle_earn(self) -> bool:
        earn_result = self.device_ui(
            description="Earn",
            packageName=self.package_name,
        ).click_exists(UI_TIMEOUT)

        if not earn_result:
            logger.error(f"[{self.device_name}] Switch to Earn tasks failed")
            return False
        logger.info(f"[{self.device_name}] Switch to Earn tasks successfully")

        self._handle_weekly_in_earn()

        new_flag = True
        socials_flag = True
        academy_flag = True
        result_flag = False
        while True:
            if new_flag:
                new_flag = self._process_task_in_earn("New")

            if socials_flag:
                socials_flag = self._process_task_in_earn("Socials")

            if academy_flag:
                academy_flag = self._process_task_in_earn("Academy")

            if new_flag or socials_flag or academy_flag:
                result_flag = True
            else:
                break
        return result_flag

    def _handle_weekly_in_earn(self):
        try:
            logger.info(f"[{self.device_name}] Processing tasks in Weekly")

            btn_open_social = self.device_ui(
                text="Earn for checking socials",
                packageName=self.package_name,
            ).sibling(
                text="Open",
                clickable=True,
            ).click_exists(UI_TIMEOUT // 2)
            if not btn_open_social:
                logger.error(f"[{self.device_name}] not found Open btn")
                return
            if self._process_start_btn_in_earn(
                start_btn_path=START_WEEKLY_ITEM_PATH
            ):
                time.sleep(5)
            self._process_claim_btn_in_earn()
            # close
            self.device_ui(
                className="android.app.Dialog",
                packageName=self.package_name,
            ).child(
                className="android.widget.Button"
            ).click_exists(UI_TIMEOUT // 2)
        except Exception as e:
            logger.error(f"[{self.device_name}] Error processing tasks in Weekly:", e)

    def _process_task_in_earn(self, tab_name: Literal["New", "Socials", "Academy"]):
        logger.info(f"[{self.device_name}] Processing tasks in {tab_name}")

        tab_ui = self.device_ui(
            text=tab_name,
            packageName=self.package_name,
        ).click_exists()
        if not tab_ui:
            logger.error(f"[{self.device_name}] Press {tab_name} tab failed")
            return False
        logger.info(f"[{self.device_name}] Press {tab_name} tab successfully")
        scrollable_view = self.device_ui(
            resourceId="app", packageName=self.package_name
        ).child(scrollable=True)
        scrollable_view.scroll(dimention="down", steps=20)
        scrollable_view.scroll(dimention="down", steps=20)

        result_flag = False
        retry = 3
        while True:
            flag = self._process_start_btn_in_earn(start_btn_path=START_ITEM_PATH)
            retry -= 1
            if not flag or retry <= 0:
                break
            result_flag = True

        retry = 3
        while True:
            flag = self._process_verify_btn_in_earn()
            if not flag or retry <= 0:
                break
            result_flag = True

        if self._process_claim_btn_in_earn():
            result_flag = True

        logger.info(
            f"[{self.device_name}] Finished processing check task for tab: {tab_name}"
        )
        return result_flag

    def _process_claim_btn_in_earn(self, threshold: float = 0.98):
        flag = False
        btn_claim_list = self.find_items(
            CLAIM_ITEM_PATH, threshold=threshold, add_x=2, add_y=2
        )

        if not btn_claim_list:
            logger.info(f"[{self.device_name}] No Claim task found")
            return False
        btn_claim_list.sort(reverse=True)

        for (x, y) in btn_claim_list:
            self.device_ui.click(x, y)
            logger.info(f"[{self.device_name}] Press Claim task successfully")
            time.sleep(3)
            flag = True
        return flag

    def _process_start_btn_in_earn(self, start_btn_path: str):
        btn_start_list = self.find_items(
            start_btn_path, add_x=2, add_y=2
        )
        if not btn_start_list:
            logger.info(f"[{self.device_name}] No Start task found")
            return False

        btn_start_list.sort(reverse=True)

        flag = False
        for (x, y) in btn_start_list:
            self.device_ui.click(x, y)
            logger.info(f"[{self.device_name}] Press Start task successfully")
            time.sleep(5)
            flag = True
            if self._get_current_package_name() != self.package_name:
                # Case: open other app
                logger.info(f"[{self.device_name}] Back task from other app")
                self.device_ui.press("recent")
                self.device_ui.swipe_ext("up", duration=0.025)
                self.device_ui.press("recent")

            else:
                logger.info(f"[{self.device_name}] Back task from tele app")
                self.back_to_a_screen()
                self._open_web_tabs_if_close()
        return flag

    def _process_verify_btn_in_earn(self):
        flag = False
        instance = 0
        while self.device_ui(
            text="Verify",
            clickable=True,
            enabled=True,
            instance=instance,
            packageName=self.package_name,
        ).exists(UI_TIMEOUT // 2):
            task_name = (
                self.device_ui(
                    text="Verify",
                    clickable=True,
                    enabled=True,
                    instance=instance,
                    packageName=self.package_name,
                )
                .sibling(
                    className="android.widget.TextView",
                )
                .get_text(timeout=UI_TIMEOUT // 10)
            )
            text_key = TASK_TO_VERIFY_DICT.get(task_name, None)
            if not text_key:
                logger.error(
                    f"[{self.device_name}] Can't find task key for `{task_name}`"
                )
                self._notify_to_tele(
                    f"[{self.device_name}] Can't find task key for `{task_name}`"
                )
                instance += 1
                if instance > 3:
                    logger.error(
                        f"[{self.device_name}] Can't find task key"
                        f" for `{task_name}` after 3 attempts"
                    )
                    return False
                continue

            btn_verify = self.device_ui(
                text="Verify",
                clickable=True,
                enabled=True,
                instance=instance,
                packageName=self.package_name,
            ).click_exists(timeout=UI_TIMEOUT // 10)
            if not btn_verify:
                logger.error(
                    f"[{self.device_name}] Press Verify for '{task_name}' failed"
                )
                return False

            logger.info(
                f"[{self.device_name}] Press Verify for '{task_name}' successfully"
            )
            time.sleep(3)
            txt_editer = self.find_items(KEYWORD_ITEM_PATH, add_x=1, add_y=1)
            if not txt_editer:
                logger.error(
                    f"[{self.device_name}] Open verification text editor failed"
                )
                self.back_to_a_screen()
                return False
            self.device_ui.click(*txt_editer[0])
            btn_verify = self.find_items(VERIFY_ITEM_PATH, add_x=1, add_y=1)
            if not btn_verify:
                logger.error(
                    f"[{self.device_name}] Not found btn Verify for '{task_name}'"
                )
                self.back_to_a_screen()
                return False

            self.device_ui.send_keys(text_key)
            time.sleep(10)
            self.device_ui.click(*btn_verify[0])
            time.sleep(3)
            btn_verify = self.find_items(VERIFY_ITEM_PATH, add_x=1, add_y=1)
            if btn_verify:
                logger.error(f"[{self.device_name}] Incorrect keyword for {task_name}")
                self.back_to_a_screen()
            logger.info(f"[{self.device_name}] Finsih entered keyword for {task_name}")
        return flag

    def _open_web_tabs_if_close(self):
        self.device_ui(description="Web tabs Blum").click_exists(10)
