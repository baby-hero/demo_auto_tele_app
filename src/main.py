import time
from datetime import datetime
from typing import Dict, List, Tuple

import uiautomator2 as u2
from adbutils._device import AdbDevice, WindowSize
from uiautomator2 import Device

from services.blum_service import BlumService
from services.hamster_kombat_service import HamsterKombatService
from src import configs
from src.services.bnb_moonbix_service import BnbMoonBixService
from src.services.side_fans_service import SideFansService
from src.utils import adb_util, common_util, notify_util
from src.utils.log_util import logger


def run_main():
    old_device_to_balance_dict = {}
    general_configs: dict = {}
    waiting_times_seconds = 3600
    while True:
        # daily tasks
        start_time = datetime.now()
        run_every_day(
            general_configs,
            old_device_to_balance_dict,
        )
        duration_seconds = (datetime.now() - start_time).seconds
        if duration_seconds < waiting_times_seconds:
            sleep_times = waiting_times_seconds - duration_seconds
            logger.info(f"Waiting for {sleep_times} minutes...")
            time.sleep(sleep_times)

        random_sleep_minus = common_util.random_int(1, 5)
        logger.info(f"Waiting for random in {random_sleep_minus} minutes...")
        time.sleep(random_sleep_minus * 60)

        while datetime.now().hour in configs.IGNORE_HOUR_RUN_LIST:
            logger.info(
                "Waiting for 1 HOUR, because current_hour "
                f"in ignore_run: {configs.IGNORE_HOUR_RUN_LIST}"
            )
            time.sleep(3600)


def run_every_day(
    general_configs: dict,
    old_device_to_balance_dict: Dict,
):
    logger.info("Start all devices")
    run_device_list: List[Tuple[Device, WindowSize, str]] = get_device_list()

    device_to_balance_dict: Dict[str, int] = {}
    for (device_ui, device_size, serial_no) in run_device_list:
        logger.info(f"[{serial_no}] START on device")
        logger.info("================================================================")
        moonbix_servie = BnbMoonBixService(
            device_ui, serial_no, device_size, general_configs
        )
        moonbix_servie.run_app(device_to_balance_dict)

        sidefans_service = SideFansService(device_ui, serial_no, general_configs)
        sidefans_service.run_app()

        blum_service = BlumService(device_ui, serial_no)
        blum_service.run_app()

        hamster_kombat_service = HamsterKombatService(device_ui, serial_no)
        hamster_kombat_service.run_app()
        hamster_kombat_service.device_ui.app_stop_all()
        hamster_kombat_service.close_tele_app()
        logger.info(f"[{serial_no}] FINISH on device")
        logger.info("================================================================")

    msgs = []
    for device, balances in device_to_balance_dict.items():
        old_balances = old_device_to_balance_dict.get(device, 0)
        if old_balances != balances:
            msgs.append(
                f"Device: {device[10:]}: {balances} "
                f"({balances - old_balances}) points\n"
            )
            old_device_to_balance_dict[device] = balances
    if msgs:
        notify_util.send_telegram_log("".join(msgs))
    logger.info("All devices checked and updated")


def get_device_list() -> List[Tuple[Device, WindowSize, str]]:
    result: List[Tuple[Device, WindowSize, str]] = []
    devices: List[AdbDevice] = adb_util.get_devices()
    for device in devices:
        serial_no = device.get_serialno()
        device_size = device.window_size()
        device_ui: Device = u2.connect_usb(serial_no)
        result.append((device_ui, device_size, serial_no))
    return result


if __name__ == "__main__":
    run_main()
