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
    while True:
        run_device_list: List[Tuple[Device, WindowSize, str]] = get_device_list()
        moonbix_servies = get_bnb_moonbix_services(run_device_list)
        sidefans_services = get_sidefans_services(run_device_list)
        blum_services = get_blum_services(run_device_list)
        hamster_kombat_services = get_hamster_kombat_services(run_device_list)
        # daily tasks
        run_every_day(
            sidefans_services,
            blum_services,
            moonbix_servies,
            hamster_kombat_services,
            old_device_to_balance_dict,
        )


def run_every_day(
    sidefans_services: List[SideFansService],
    blum_services: List[BlumService],
    moonbix_servies: List[BnbMoonBixService],
    hamster_kombat_services: List[HamsterKombatService],
    old_device_to_balance_dict: Dict,
    waiting_times_minus: int = 70,
):
    start_time = datetime.now()
    for i in range(len(sidefans_services)):
        sidefans_services[i].run_app()
        blum_services[i].run_app()
        hamster_kombat_services[i].run_app()
        hamster_kombat_services[i].close_tele_app()

    while True:
        try:
            device_to_balance_dict: Dict[str, int] = {}
            for item in moonbix_servies:
                item.run_app(device_to_balance_dict)
                item.close_tele_app()

            # notify telegram
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
        except Exception as e:
            logger.error("error", e)
            notify_util.send_telegram_log(f"have error: {str(e)}")

        random_sleep_minus = common_util.random_int(2, 5)
        logger.info(f"Waiting for random in {random_sleep_minus} minutes...")
        time.sleep(random_sleep_minus * 60)
        logger.info(f"Waiting for {waiting_times_minus} minutes...")
        time.sleep(waiting_times_minus * 60)
        while datetime.now().hour in configs.IGNORE_HOUR_RUN_LIST:
            logger.info(
                "Waiting for 1 HOUR, because current_hour "
                f"in ignore_run: {configs.IGNORE_HOUR_RUN_LIST}"
            )
            time.sleep(3600)
        if (datetime.now() - start_time).seconds >= 8 * 3600:
            notify_util.send_telegram_log("Stop function and rerun again.")
            logger.info("Stop run_every_day and rerun again.")
            return


def get_device_list() -> List[Tuple[Device, WindowSize, str]]:
    result: List[Tuple[Device, WindowSize, str]] = []
    devices: List[AdbDevice] = adb_util.get_devices()
    for device in devices:
        serial_no = device.get_serialno()
        device_size = device.window_size()
        device_ui: Device = u2.connect_usb(serial_no)
        result.append((device_ui, device_size, serial_no))
    return result


def get_bnb_moonbix_services(
    device_list: List[Tuple[Device, WindowSize, str]]
) -> List[BnbMoonBixService]:
    result: List[BnbMoonBixService] = []
    for (device_ui, device_size, serial_no) in device_list:
        item = BnbMoonBixService(device_ui, serial_no, device_size)
        result.append(item)
    return result


def get_sidefans_services(
    device_list: List[Tuple[Device, WindowSize, str]]
) -> List[SideFansService]:
    result = []
    for (device_ui, _, serial_no) in device_list:
        item = SideFansService(device_ui, serial_no)
        result.append(item)
    return result


def get_blum_services(
    device_list: List[Tuple[Device, WindowSize, str]]
) -> List[BlumService]:
    result = []
    for (device_ui, _, serial_no) in device_list:
        item = BlumService(device_ui, serial_no)
        result.append(item)
    return result


def get_hamster_kombat_services(
    device_list: List[Tuple[Device, WindowSize, str]]
) -> List[HamsterKombatService]:
    result = []
    for (device_ui, _, serial_no) in device_list:
        item = HamsterKombatService(device_ui, serial_no)
        result.append(item)
    return result


if __name__ == "__main__":
    run_main()
