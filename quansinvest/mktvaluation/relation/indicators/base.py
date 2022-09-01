from abc import ABC, abstractmethod


class AbstractIndicator(ABC):
    def __init__(self, name: str):
        self.data = self.get_data(name)
        self.name = name

    @abstractmethod
    def get_data(self, name: str):
        raise NotImplementedError
