import random
from typing import Union

import yaml
from pydantic import BaseModel


def parse_model_config(
    object_or_path: Union[dict, str], pydantic_cls: BaseModel, is_list: bool = False
):
    if isinstance(object_or_path, dict):
        return pydantic_cls(**object_or_path)
    if isinstance(object_or_path, str):
        with open(object_or_path, "r") as file:
            data = yaml.safe_load(file)
            if is_list:
                return [pydantic_cls.model_validate(item) for item in data]
            return pydantic_cls.model_validate(data)
    raise ValueError(f"Invalid input value: {object_or_path}")


def random_int(min_value: int, max_value: int) -> int:
    return random.randint(min_value, max_value)


def random_float_in_range(min_value: float = 0.3, max_value: float = 1.2) -> float:
    return random.uniform(min_value, max_value)
