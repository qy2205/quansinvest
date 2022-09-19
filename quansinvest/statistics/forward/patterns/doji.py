"""
default vol = 2%, short_diff = 0.2%, open_close_diff = 0.1%
pre-requisite: (high - low)/low > vol
1. gravestone doji (high > close * (1 + vol - short_diff), low < close*(1 - short_diff), |daily_return| < open_close_diff)
2. long legged doji (high > close * (1 + vol/2), low < close*(1 - vol/2), |daily_return| < open_close_diff)
3. dragonfly doji (high > close * (1 + short_diff), low < close*(1 - vol + short_diff), |daily_return| < open_close_diff)
wiki: https://www.investopedia.com/terms/d/doji.asp
"""
from .base import AbstractPattern
from quansinvest.data.constants import (
    CLOSE_PRICE_COLUMN_NAME,
    OPEN_PRICE_COLUMN_NAME,
    DAILY_RETURN_COLUMN_NAME,
    HIGH_PRICE_COLUMN_NAME,
    LOW_PRICE_COLUMN_NAME,
)


class DojiPattern(AbstractPattern):

    available_types = ["dragonfly", "gravestone", "long_legged"]

    def __init__(
        self,
        vol: float = 0.02,
        short_diff: float = 0.002,
        open_close_diff: float = 0.001,
        pattern_type: str = "dragonfly",
    ):
        self.vol = vol
        self.short_diff = short_diff
        self.open_close_diff = open_close_diff
        self.pattern_type = pattern_type

    @property
    def look_back_period(self):
        return 1

    def _is_dragonfly(self, high, low, close, ret):
        if high > close * (1 + self.vol - self.short_diff) and \
                low < close * (1 - self.short_diff) and \
                abs(ret) < self.open_close_diff:
            return True
        else:
            return False

    def _is_gravestone(self, high, low, close, ret):
        if high > close * (1 + self.vol/2) and \
                low < close*(1 - self.vol/2) and \
                abs(ret) < self.open_close_diff:
            return True
        else:
            return False

    def _is_long_legged(self, high, low, close, ret):
        if high > close * (1 + self.short_diff) and \
                low < close*(1 - self.vol + self.short_diff) and \
                abs(ret) < self.open_close_diff:
            return True
        else:
            return False

    def is_form(self, period_df, cur_pos):
        data_dict = period_df.to_dict(orient="records")[0]
        close_price = data_dict[CLOSE_PRICE_COLUMN_NAME]
        high_price = data_dict[HIGH_PRICE_COLUMN_NAME]
        low_price = data_dict[LOW_PRICE_COLUMN_NAME]
        daily_return = data_dict[DAILY_RETURN_COLUMN_NAME]
        if self.pattern_type == "dragonfly":
            return self._is_dragonfly(high_price, low_price, close_price, daily_return)
        elif self.pattern_type == "gravestone":
            return self._is_gravestone(high_price, low_price, close_price, daily_return)
        elif self.pattern_type == "long_legged":
            return self._is_long_legged(high_price, low_price, close_price, daily_return)
