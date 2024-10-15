from typing import Dict, Optional

from pydantic import BaseModel


class ConfigDevice(BaseModel):
    device_name: str

    is_blum: bool = False
    blum_group_id: Optional[int] = None
    blum_delay_interval: Optional[int] = 8 * 60 * 60

    is_hamster_kombat: bool = False
    hamster_kombat_group_id: Optional[int] = None
    hamster_kombat_delay_interval: Optional[int] = 6 * 60 * 60

    is_bnb_moonbix: bool = False
    bnb_moonbix_group_id: Optional[int] = None
    bnb_moonbix_delay_interval: Optional[int] = 2 * 60 * 60

    is_side_fans: bool = False
    side_fans_group_id: Optional[int] = None
    side_fans_delay_interval: Optional[int] = 8 * 60 * 60

    last_running_ts_by_group_id: Optional[Dict[int, int]] = {}

    notify_error_tele: bool = False
    notify_info_tele: bool = False
    notify_warning_tele: bool = False
