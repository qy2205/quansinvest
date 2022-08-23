from abc import ABC, abstractmethod
import pandas as pd


class AbstractForm(ABC):
    @property
    @abstractmethod
    def look_back_period(self):
        raise NotImplementedError

    @abstractmethod
    def is_form(self, df: pd.DataFrame, cur_pos: int) -> bool:
        """
        :param df: dataframe with date, open, high, low, close
        :param cur_pos: current pos
        :return: boolean, whether the current pos + look back period a form
        """
        raise NotImplementedError
