import time

from uiautomator2 import Device

from src.configs import UI_TIMEOUT
from src.services.tele_service import BaseTeleGroupService
from src.utils.log_util import logger


class HamsterKombatService(BaseTeleGroupService):
    def __init__(
        self, device_ui: Device, serial_no: str, general_configs: dict
    ) -> None:
        super().__init__(device_ui, serial_no, general_configs)
        self.group_name = "Hamster Kombat"
        self.waiting_next_run_interval = 6 * 60 * 60
        logger.info(f"[{self.serial_no}] Init {self.group_name} in {self.app_name}")

    def get_group_index(self) -> int:
        """Find group index in tele app start_index from 0"""
        return 2

    def _waiting_bot_menu_loaded(self) -> bool:
        logger.info(f"[{self.serial_no}] Waiting for bot menu loaded")
        self.device_ui(
            description="Exchange",
            packageName=self.package_name,
        ).wait(timeout=self.bot_menu_timeout)
        return True

    def run_app(self) -> bool:
        try:
            if not self._check_run_app():
                logger.info(f"[{self.serial_no}] Ignore running app {self.group_name}")
                return False
            if not self.start_group():
                return False

            self._claim_daily_rewards()
            self._handle_earn_tasks()
            self._handle_background_tasks()

            self._set_pre_run_at()
            return self.end_group()
        except Exception as e:
            logger.error(f"[{self.serial_no}] Error running app {self.app_name}:", e)
            return False

    def _claim_daily_rewards(self) -> bool:
        result = self.device_ui(
            textStartsWith="Thank you, ",
            clickable=True,
            packageName=self.package_name,
        ).click_exists(UI_TIMEOUT // 2)
        if result:
            logger.info(f"[{self.serial_no}] Claim daily rewards successfully")
        else:
            logger.error(f"[{self.serial_no}] claim daily rewards failed or claimed")
            return False
        return True

    def _handle_earn_tasks(self) -> bool:
        earn_result = self.device_ui(
            description="Earn",
            clickable=True,
            packageName=self.package_name,
        ).click_exists(UI_TIMEOUT)

        if not earn_result:
            logger.error(f"[{self.serial_no}] Press Earn tasks failed")
            return False

        logger.info(f"[{self.serial_no}] Press Earn tasks successfully")

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
            logger.error(f"[{self.serial_no}] Not foud task index {task_index}")
        else:
            logger.info(
                f"[{self.serial_no}] Click task index {task_index} successfully"
            )

        btn_check_result = self.device_ui(
            text="Check",
            clickable=True,
            enabled=True,
            packageName=self.package_name,
        ).click_exists(UI_TIMEOUT // 4)
        if not btn_check_result:
            logger.error(f"[{self.serial_no}] Press Check button not found")
        else:
            logger.info(f"[{self.serial_no}] Press check rewards successfully")

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
        ).exists(UI_TIMEOUT // 4):
            self.back_to_a_screen()

        logger.info(f"[{self.serial_no}] Finished task index {task_index}")

    def _handle_background_tasks(self) -> bool:
        background_result = self.device_ui(
            description="Playground",
            clickable=True,
            packageName=self.package_name,
        ).click_exists(UI_TIMEOUT // 2)

        if not background_result:
            logger.error(f"[{self.serial_no}] Press Background tasks failed")
            return False

        logger.info(f"[{self.serial_no}] Press Background tasks successfully")

        mine_cards = self.device_ui(
            text="Mine cards",
            clickable=True,
            packageName=self.package_name,
        ).click_exists(UI_TIMEOUT // 2)

        if not mine_cards:
            logger.error(f"[{self.serial_no}] Not foud Mine cards")
            return False

        logger.info(f"[{self.serial_no}] Click Mine cards successfully")
        self._check_and_buy_new_cards_tab()
        self._check_and_buy_my_cards_tab()
        logger.info(f"[{self.serial_no}] Finished check and buy cards")

        return True

    def _check_and_buy_new_cards_tab(self):
        logger.info(f"[{self.serial_no}] Start check and buy new cards")
        while True:
            if not self._check_and_buy_new_card():
                break
            time.sleep(3)

        logger.info(f"[{self.serial_no}] Finished check and buy new cards")

    def _check_and_buy_new_card(self) -> bool:
        switch_new_card_tab = self.device_ui(
            text="New cards", clickable=True, packageName=self.package_name
        ).click_exists(UI_TIMEOUT // 2)
        if not switch_new_card_tab:
            logger.error(f"[{self.serial_no}] Press New cards tab failed")
            return False
        logger.info(f"[{self.serial_no}] Press New cards tab successfully")

        if self.device_ui(
            text="Profit per hour", packageName=self.package_name
        ).click_exists(UI_TIMEOUT // 2):
            if self.device_ui(
                text="Go ahead",
                enabled=True,
                clickable=True,
                packageName=self.package_name,
            ).click_exists(UI_TIMEOUT // 2):
                logger.info(f"[{self.serial_no} Buy new card successful")
                return True

            self.device_ui(
                text="Mine cards", packageName=self.package_name
            ).click_exists(UI_TIMEOUT // 4)
        return False

    def _check_and_buy_my_cards_tab(self):
        tab_result = self.device_ui(
            text="My cards", clickable=True, packageName=self.package_name
        ).click_exists(UI_TIMEOUT // 2)

        if not tab_result:
            logger.error(f"[{self.serial_no}] Not foud  My cards Tab")
            return False

        logger.info(f"[{self.serial_no}] Click My cards Tab successfully")
        time.sleep(10)
        # get minimum and maximum of screen:
        top_limit = self.device_ui(
            text="Mine cards",
            packageName=self.package_name,
        ).bounds()[3]
        bottom_limit = self.device_ui(
            description="Playground",
            packageName=self.package_name,
        ).bounds()[1]
        logger.info(f"[{self.serial_no}] Start check and buy cards")
        self.check_and_buy_cards_of_current_page(
            top_limit=top_limit, bottom_limit=bottom_limit
        )

        scrollable_view = self.device_ui(scrollable=True, packageName=self.package_name)
        page_index = 1
        if scrollable_view.exists(UI_TIMEOUT // 2):
            logger.info(
                f"[{self.serial_no}] Start scroll to check and buy cards"
                f" with number scroll: {scrollable_view.count}"
            )
            flag = True
            while True:
                # scroll down to load more cards
                flag = scrollable_view.scroll(direction="down", steps=20)
                logger.info(f"[{self.serial_no}] Page {page_index} loaded")
                page_index += 1
                self.check_and_buy_cards_of_current_page(
                    page_index=page_index,
                    top_limit=top_limit,
                    bottom_limit=bottom_limit,
                )
                if not flag:
                    break
        else:
            logger.error(f"[{self.serial_no}] Not found scrollable view")

    def check_and_buy_cards_of_current_page(
        self,
        page_index=0,
        top_limit: int = 0,
        bottom_limit: int = 5000,
    ):
        if not self.device_ui(
            text="Profit per hour", packageName=self.package_name
        ).exists(UI_TIMEOUT):
            logger.info(f"[{self.serial_no}] Not found cards in page {page_index}")
            return False
        bound_cards = []
        for card in self.device_ui(
            text="Profit per hour", packageName=self.package_name
        ):
            card_bounds = card.bounds()
            card_x = (card_bounds[0] + card_bounds[2]) // 2
            card_y = (card_bounds[1] + card_bounds[3]) // 2
            logger.info(f"[{self.serial_no}] Found cards at ({card_x}, {card_y})")
            bound_cards.append((card_x, card_y))
        count = 0
        logger.info(
            f"[{self.serial_no}] Start check {len(bound_cards)} cards "
            f"in page: {page_index}"
        )
        for (card_x, card_y) in bound_cards:
            logger.info(
                f"[{self.serial_no}] Check card ({card_x}, {card_y}) "
                f"in page: {page_index}"
            )
            if card_y > top_limit:
                if card_y >= bottom_limit:
                    card_y = card_y - ((card_y - bottom_limit) + 50)
                self.device_ui.click(card_x, card_y)
                if self.device_ui(
                    text="Go ahead",
                    enabled=True,
                    clickable=True,
                    packageName=self.package_name,
                ).click_exists(UI_TIMEOUT // 4):
                    count += 1
                    logger.info(
                        f"[{self.serial_no} Update {count} card successful "
                        f"in page {page_index}"
                    )
                    time.sleep(3)
            logger.info(f"[{self.serial_no} Back to main page")
            self.device_ui(
                text="Mine cards", packageName=self.package_name
            ).click_exists(UI_TIMEOUT // 4)

        logger.info(f"[{self.serial_no}] Finished buy cards in page: {page_index}")
