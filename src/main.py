import time
from datetime import datetime
from typing import List, Tuple

import uiautomator2 as u2
from adbutils._device import AdbDevice, WindowSize
from uiautomator2 import Device

from src import configs
from src.services.bnb_moonbix_service import BnbMoonBixService
from src.services.side_fans_service import SideFansService
from src.utils import adb_util, common_util, notify_util
from src.utils.log_util import logger


def run_main():
    waiting_times_minus = 38
    old_device_to_balance_dict = {}
    run_device_list: List[Tuple[Device, WindowSize, str]] = get_device_list()
    # daily tasks
    for item in run_device_list:
        side_fans_daily_checkin(item)

    moonbix_servies = get_bnb_moonbix_services(run_device_list)
    while True:
        try:
            device_to_balance_dict = {}
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


def side_fans_daily_checkin(item) -> bool:
    try:
        side_fans_service = SideFansService(item[0], item[2])
        return side_fans_service.run_app()
    except Exception as e:
        logger.error("daily tasks", e)
    return False


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


if __name__ == "__main__":
    run_main()
