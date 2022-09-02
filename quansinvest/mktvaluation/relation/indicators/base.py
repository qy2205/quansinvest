from abc import ABC, abstractmethod
from quansinvest.utils.utils import classproperty


class AbstractIndicator(ABC):
    available_names = []
    _symbols = []

    def __init__(self, name: str):
        if name not in AbstractIndicator.available_names:
            print(f"Only the following names available: {AbstractIndicator.available_names}")
            raise NotImplementedError

        self.data = self._get_data(name)
        self.name = name

    @classproperty
    def names_symbols_map(cls):
        return dict(zip(cls.available_names, cls._symbols))

    @abstractmethod
    def _get_data(self, name: str):
        raise NotImplementedError
