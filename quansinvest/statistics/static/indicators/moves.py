import pandas as pd
from quansinvest.data.constants import (
    DAILY_RETURN_COLUMN_NAME,
)


class MoveUpIndicator:
    def __init__(self, data: pd.DataFrame, return_threshold: float, name: str = "move_up"):
        self.data = self._get_results(data, return_threshold)
        self.name = name

    @staticmethod
    def _get_results(data, return_threshold):
        """
        :param data: pandas DataFrame
        :param return_threshold: if daily return >= return_threshold
        :return: pd.DataFrame
        """
        return data[data[DAILY_RETURN_COLUMN_NAME] >= return_threshold]


class MoveDownIndicator:
    def __init__(self, data: pd.DataFrame, return_threshold: float, name: str = "move_down"):
        self.data = self._get_results(data, return_threshold)
        self.name = name

    @staticmethod
    def _get_results(data, return_threshold):
        """
        :param data: pandas DataFrame
        :param return_threshold: if daily return <= return_threshold
        :return: pd.DataFrame
        """
        return data[data[DAILY_RETURN_COLUMN_NAME] <= return_threshold]
