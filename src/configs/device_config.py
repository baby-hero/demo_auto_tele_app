from typing import Dict, List

import yaml

from model.config_device import ConfigDevice
from src.utils import common_util

DEVICE_FILE_PATH = "resources/yaml/device.yaml"


def load_config_devices(filename):
    with open(filename, "r") as file:
        data = yaml.safe_load(file)
        return [ConfigDevice(**item) for item in data]


CONFIG_DEVICES: List[ConfigDevice] = common_util.parse_model_config(
    DEVICE_FILE_PATH, ConfigDevice, is_list=True
)


NAME_TO_CONFIG_DEVICE_MAP: Dict[str, ConfigDevice] = {
    device.device_name: device for device in CONFIG_DEVICES
}
