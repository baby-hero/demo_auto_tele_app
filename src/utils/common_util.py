import random


def random_int(min_value: int, max_value: int) -> int:
    return random.randint(min_value, max_value)


def random_float_in_range(min_value: float = 0.5, max_value: float = 1.4) -> float:
    return random.uniform(min_value, max_value)
