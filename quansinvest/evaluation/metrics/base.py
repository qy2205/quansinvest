from abc import ABC, abstractmethod


class BaseMetrics(ABC):
    name = "base"
    freq_map = {
        "D": 252,
        "W": 52,
        "M": 12,
        "Q": 4,
        "Y": 1,
    }

