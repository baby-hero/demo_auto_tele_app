from typing import List, Tuple

from adbutils import AdbClient
from adbutils._device import AdbDevice, WindowSize

from src.configs import ADB_HOST, ADB_PORT
from src.utils.common_util import random_int

adb: AdbClient = AdbClient(host=ADB_HOST, port=ADB_PORT)


def get_devices() -> List[AdbDevice]:
    devices = adb.device_list()
    return devices


def get_random_position_to_click(device_size: WindowSize) -> Tuple[int, int]:
    min_value = -int(device_size.width * 0.2)
    max_value = -min_value
    add_width = random_int(min_value, max_value)
    add_height = random_int(min_value, max_value)
    return (
        device_size.width // 2 + add_width,
        device_size.height // 3 + add_height,
    )


class AdbService:
    def __init__(self, adb_device: AdbDevice):
        self.adb_device = adb_device
        self.device_size = self.adb_device.window_size()

    def get_device_size(self) -> WindowSize:
        return self.adb_device.window_size()

    def get_random_position_to_click(self) -> Tuple[int, int]:
        min_value = -int(self.device_size.width * 0.2)
        max_value = -min_value
        add_width = random_int(min_value, max_value)
        add_height = random_int(min_value, max_value)
        return (
            self.device_size.width // 2 + add_width,
            self.device_size.height // 3 + add_height,
        )

    def swipe_to_left(self):
        self.adb_device.swipe(
            self.device_size.width * 0.9,
            self.device_size.height // 2,
            self.device_size.width * 0.1,
            self.device_size.height // 2,
            100,
        )
