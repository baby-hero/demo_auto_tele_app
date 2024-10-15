import concurrent.futures
import time
from datetime import datetime
from typing import Optional, Tuple

import uiautomator2 as u2
from adbutils._device import WindowSize
from uiautomator2 import Device

from configs import common_config
from model.config_device import ConfigDevice
from services.blum_service import BlumService
from services.hamster_kombat_service import HamsterKombatService
from services.tele_service import BaseTeleService
from src.configs.device_config import NAME_TO_CONFIG_DEVICE_MAP
from src.services.bnb_moonbix_service import BnbMoonBixService
from src.services.side_fans_service import SideFansService
from src.utils import adb_util, common_util, device_util, notify_util
from src.utils.log_util import logger


# TODO: CHECK time run on app after run device
def run_on_devce(device_ui, device_size, device_name, config_device: ConfigDevice):
    logger.info("================================================================")
    logger.info(f"[{device_name}] START on device")
    logger.info("================================================================")
    flag = True

    if not config_device:
        raise ValueError(f"Not found config device name {device_name}")

    tele_service_instance: BaseTeleService = None

    if config_device.is_bnb_moonbix:
        moonbix_servie = BnbMoonBixService(
            device_ui, device_name, device_size, config_device
        )
        tele_service_instance = moonbix_servie
        if not moonbix_servie.run_app():
            flag = False
    if config_device.is_side_fans:
        sidefans_service = SideFansService(device_ui, device_name, config_device)
        tele_service_instance = sidefans_service
        if not sidefans_service.run_app():
            flag = False
    if config_device.is_blum:
        blum_service = BlumService(device_ui, device_name, config_device)
        tele_service_instance = blum_service
        if not blum_service.run_app():
            flag = False
    if config_device.is_hamster_kombat:
        hamster_kombat_service = HamsterKombatService(
            device_ui, device_name, config_device
        )
        tele_service_instance = hamster_kombat_service
        if not hamster_kombat_service.run_app():
            flag = False

    if tele_service_instance:
        tele_service_instance.device_ui.app_stop_all()
        time.sleep(10)
        tele_service_instance.close_tele_app()
    time.sleep(10)
    logger.info(
        f"[{device_name}] FINISH on device: {config_device.last_running_ts_by_group_id}"
    )
    logger.info("================================================================")
    return flag


def worker_function(
    vm,
    start_index,
    running_serial_no_set: set,
) -> bool:
    vm_name, vm_uid = vm
    serial_no = vm_name
    try:
        config_device = NAME_TO_CONFIG_DEVICE_MAP.get(vm_name, None)
        if config_device is None:
            logger.error(f"[{vm_name}] Can't find config device name {vm_name}")
            running_serial_no_set.add(vm_name)
            return (vm_name, None)

        flag, select_device_info = start_vm_and_waiting_get_new_device_info(
            start_index, vm_name, vm_uid, running_serial_no_set
        )
        if not flag:
            logger.error(f"[{vm_name}] Failed to find new device")
            running_serial_no_set.add(vm_name)
            return (vm_name, False)

        logger.info("================================================================")
        (device_ui, device_size, serial_no) = select_device_info
        logger.info(f"[{vm_name}] Start new device: {serial_no}.")
        logger.info(f"{running_serial_no_set}=================")

        result = run_on_devce(device_ui, device_size, vm_name, config_device)
        return (vm_name, result)
    except Exception as e:
        logger.error(f"[{vm_name}] Error running device: {serial_no}:", e)
        running_serial_no_set.add(vm_name)
        return (vm_name, False)

    finally:
        device_util.stop_vm(vm_name, vm_uid)
        logger.info(f"[{vm_name}] Finish device: {serial_no}")
        logger.info("================================================================")


def start_vm_and_waiting_get_new_device_info(
    start_index, vm_name, vm_uid, running_serial_no_set: set, wait_ts=30, retry=10
) -> Tuple[bool, Optional[Tuple[Device, WindowSize, str]]]:
    count = 0
    while len(running_serial_no_set) < start_index:
        logger.info(
            f"[{vm_name}] waiting in {wait_ts} seconds] retry: {count}"
            f" with index: {start_index} and set: {running_serial_no_set}"
        )
        time.sleep(30)
        count += 1
        if count > retry:
            logger.error(f"[{vm_name}] Failed to find new device after {retry} retries")
            return (False, None)

    device_util.start_vm(vm_name, vm_uid)
    count = 0
    while True:
        time.sleep(wait_ts)
        count += 1
        if count > retry:
            logger.error(f"[{vm_name}] Timeout waiting for device: {vm_name} to start")
            break
        current_devices = adb_util.get_devices()
        logger.info(f"[{vm_name}] Current devices: {len(current_devices)}")
        for device in current_devices:
            serial_no = device.get_serialno()
            if serial_no not in running_serial_no_set:
                running_serial_no_set.add(serial_no)
                device_size = device.window_size()
                device_ui: Device = u2.connect_usb(serial_no)
                time.sleep(20)
                return (True, (device_ui, device_size, serial_no))
    return (False, None)


def main():
    mvs = device_util.get_vms()
    mvs = [mv for mv in mvs if mv[0] in NAME_TO_CONFIG_DEVICE_MAP]
    waiting_times_seconds = 3600
    while True:
        # daily tasks
        start_time = datetime.now()
        running_device_name_set = set()
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(worker_function, mvs[i], i, running_device_name_set)
                for i in range(len(mvs))
            ]

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)

        msgs = [f'"{item[0]}": {item[1]}\n' for item in results]
        notify_util.send_telegram_log("".join(msgs))

        duration_seconds = (datetime.now() - start_time).seconds
        if duration_seconds < waiting_times_seconds:
            sleep_times = waiting_times_seconds - duration_seconds
            logger.info(f"Waiting for {sleep_times // 60} minutes...")
            time.sleep(sleep_times)

        random_sleep_minus = common_util.random_int(1, 5)
        logger.info(f"Waiting for random in {random_sleep_minus} minutes...")
        time.sleep(random_sleep_minus * 60)

        while datetime.now().hour in common_config.IGNORE_HOUR_RUN_LIST:
            logger.info(
                "Waiting for 1 HOUR, because current_hour "
                f"in ignore_run: {common_config.IGNORE_HOUR_RUN_LIST}"
            )
            time.sleep(3600)


if __name__ == "__main__":
    main()
