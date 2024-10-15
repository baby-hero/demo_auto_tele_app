import time

from uiautomator2 import Device

from model.config_device import ConfigDevice
from src.configs.common_config import UI_TIMEOUT
from src.configs.hamster_config import GO_AHEAD_ITEM_PATH, PROFIT_PER_HOUR_ITEM_PATH
from src.services.tele_service import BaseTeleGroupService
from src.utils.log_util import logger


class HamsterKombatService(BaseTeleGroupService):
    def __init__(
        self, device_ui: Device, serial_no: str, config_device: ConfigDevice
    ) -> None:
        super().__init__(device_ui, serial_no, config_device)
        self.group_name = "Hamster Kombat"
        self.waiting_next_run_interval = config_device.hamster_kombat_delay_interval
        self.group_index = config_device.hamster_kombat_group_id
        logger.info(f"[{self.device_name}] Init {self.group_name} in {self.app_name}")

    def _waiting_bot_menu_loaded(self) -> bool:
        logger.info(f"[{self.device_name}] Waiting for bot menu loaded")
        self.device_ui(
            description="Exchange",
            packageName=self.package_name,
        ).wait(timeout=self.bot_menu_timeout)
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

            self._claim_daily_rewards()
            self._handle_earn_tasks()
            self._handle_background_tasks()

            self._set_run_last_at()
            return self.end_group()
        except Exception as e:
            logger.error(f"[{self.device_name}] Error running app {self.app_name}:", e)
            return False

    def _claim_daily_rewards(self) -> bool:
        result = self.device_ui(
            textStartsWith="Thank you, ",
            clickable=True,
            packageName=self.package_name,
        ).click_exists(UI_TIMEOUT)
        if result:
            logger.info(f"[{self.device_name}] Claim daily rewards successfully")
        else:
            logger.error(f"[{self.device_name}] claim daily rewards failed or claimed")
            return False
        return True

    def _handle_earn_tasks(self) -> bool:
        earn_result = self.device_ui(
            description="Earn",
            clickable=True,
            packageName=self.package_name,
        ).click_exists(UI_TIMEOUT)

        if not earn_result:
            logger.error(f"[{self.device_name}] Press Earn tasks failed")
            return False

        logger.info(f"[{self.device_name}] Press Earn tasks successfully")

        self._handle_earn_task(3)
        self._handle_earn_task(4)
        return True

    def _handle_earn_task(self, task_index: int):
        task_click = (
            self.device_ui(
                text="Hamster Youtube",
                packageName=self.package_name,
            )
            .sibling(index=task_index)
            .click_exists(UI_TIMEOUT)
        )
        if not task_click:
            logger.error(f"[{self.device_name}] Not foud task index {task_index}")
        else:
            logger.info(
                f"[{self.device_name}] Click task index {task_index} successfully"
            )

        btn_check_result = self.device_ui(
            text="Check",
            clickable=True,
            enabled=True,
            packageName=self.package_name,
        ).click_exists(UI_TIMEOUT // 2)
        if not btn_check_result:
            logger.error(f"[{self.device_name}] Press Check button not found")
        else:
            logger.info(f"[{self.device_name}] Press check rewards successfully")

        retry = 2
        while self.device_ui(
            text="Check",
            enabled=False,
            packageName=self.package_name,
        ).exists(UI_TIMEOUT // 2):
            self.back_to_a_screen()
            retry -= 1
            if retry == 0:
                break
        if self.device_ui(
            text="Watch video",
            packageName=self.package_name,
        ).exists(UI_TIMEOUT // 2):
            self.back_to_a_screen()

        logger.info(f"[{self.device_name}] Finished task index {task_index}")

    def _handle_background_tasks(self) -> bool:
        background_result = self.device_ui(
            description="Playground",
            clickable=True,
            packageName=self.package_name,
        ).click_exists(UI_TIMEOUT // 2)

        if not background_result:
            logger.error(f"[{self.device_name}] Press Background tasks failed")
            return False

        logger.info(f"[{self.device_name}] Press Background tasks successfully")

        mine_cards = self.device_ui(
            text="Mine cards",
            clickable=True,
            packageName=self.package_name,
        ).click_exists(UI_TIMEOUT // 2)

        if not mine_cards:
            logger.error(f"[{self.device_name}] Not foud Mine cards")
            return False

        logger.info(f"[{self.device_name}] Click Mine cards successfully")
        self._check_and_buy_new_cards_tab()
        self._check_and_buy_my_cards_tab()
        logger.info(f"[{self.device_name}] Finished check and buy cards")

        background_result = self.device_ui(
            description="Exchange",
            clickable=True,
            packageName=self.package_name,
        ).click_exists(UI_TIMEOUT // 2)
        if background_result:
            logger.info(f"[{self.device_name}] back to exchange screen successfully")
        else:
            logger.error(f"[{self.device_name}] back to exchange screen failed")
        return True

    def _check_and_buy_new_cards_tab(self):
        logger.info(f"[{self.device_name}] Start check and buy new cards")
        while True:
            if not self._check_and_buy_new_card():
                break
            time.sleep(3)

        logger.info(f"[{self.device_name}] Finished check and buy new cards")

    def _check_and_buy_new_card(self) -> bool:
        switch_new_card_tab = self.device_ui(
            text="New cards", clickable=True, packageName=self.package_name
        ).click_exists(UI_TIMEOUT // 2)
        if not switch_new_card_tab:
            logger.error(f"[{self.device_name}] Press New cards tab failed")
            return False
        logger.info(f"[{self.device_name}] Press New cards tab successfully")

        if self.device_ui(
            text="Profit per hour", packageName=self.package_name
        ).click_exists(UI_TIMEOUT // 2):
            if self.device_ui(
                text="Go ahead",
                enabled=True,
                clickable=True,
                packageName=self.package_name,
            ).click_exists(UI_TIMEOUT // 2):
                logger.info(f"[{self.device_name} Buy new card successful")
                return True

            self.device_ui(
                text="Mine cards", packageName=self.package_name
            ).click_exists(UI_TIMEOUT // 2)
        return False

    def _check_and_buy_my_cards_tab(self):
        tab_result = self.device_ui(
            text="My cards", clickable=True, packageName=self.package_name
        ).click_exists(UI_TIMEOUT // 2)

        if not tab_result:
            logger.error(f"[{self.device_name}] Not foud  My cards Tab")
            return False

        logger.info(f"[{self.device_name}] Click My cards Tab successfully")
        time.sleep(10)
        # get btn `mine card` position:
        mine_card_bounds = self.device_ui(
            text="Mine cards",
            packageName=self.package_name,
        ).bounds()
        mine_card_x = (mine_card_bounds[0] + mine_card_bounds[2]) // 2
        mine_card_y = (mine_card_bounds[1] + mine_card_bounds[3]) // 2
        mine_card_position = (mine_card_x, mine_card_y)
        logger.info(f"[{self.device_name}] Start check and buy cards")
        self.check_and_buy_cards_of_current_page(mine_card_position=mine_card_position)

        scrollable_view = self.device_ui(scrollable=True, packageName=self.package_name)
        page_index = 1
        if scrollable_view.exists(UI_TIMEOUT // 2):
            logger.info(
                f"[{self.device_name}] Start scroll to check and buy cards"
                f" with number scroll: {scrollable_view.count}"
            )
            flag = True
            while True:
                # scroll down to load more cards
                flag = scrollable_view.scroll(direction="down", steps=20)
                time.sleep(5)
                logger.info(f"[{self.device_name}] Page {page_index} loaded")
                page_index += 1
                self.check_and_buy_cards_of_current_page(
                    mine_card_position=mine_card_position,
                    page_index=page_index,
                )
                if not flag:
                    break
        else:
            logger.error(f"[{self.device_name}] Not found scrollable view")

    def check_and_buy_cards_of_current_page(
        self,
        mine_card_position,
        page_index=0,
    ):
        count = 0
        bound_cards = self.find_items(
            PROFIT_PER_HOUR_ITEM_PATH, threshold=0.8, num_div=2
        )
        if not bound_cards:
            logger.info(f"[{self.device_name}] Not found cards in page {page_index}")
            return False
        logger.info(
            f"[{self.device_name}] Start check {len(bound_cards)} cards "
            f"in page: {page_index}"
        )
        for (card_x, card_y) in bound_cards:
            logger.info(
                f"[{self.device_name}] Check card ({card_x}, {card_y}) "
                f"in page: {page_index}"
            )
            self.device_ui.click(card_x, card_y)
            time.sleep(3)
            btn_go_ahead = self.find_items(GO_AHEAD_ITEM_PATH, threshold=0.95)
            if btn_go_ahead:
                (x, y) = btn_go_ahead[0]
                self.device_ui.click(x, y)
                count += 1
                logger.info(
                    f"[{self.device_name} Update {count} card successful "
                    f"in page {page_index}"
                )
                time.sleep(3)
            else:
                logger.info(f"[{self.device_name} Back to main page")
                self.device_ui.click(*mine_card_position)
                time.sleep(1)

        logger.info(f"[{self.device_name}] Finished buy cards in page: {page_index}")
