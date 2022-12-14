"""
1. continuous move up with cum return
2. continuous move down with cum loss
3. continuous move up with single day threshold
4. continuous move down with single day threshold
3. single day surge
4. single day plummet
"""
from .base import AbstractPattern
from quansinvest.data.constants import (
    CLOSE_PRICE_COLUMN_NAME,
    OPEN_PRICE_COLUMN_NAME,
    DAILY_RETURN_COLUMN_NAME,
)


class ContinuousPattern(AbstractPattern):

    available_types = ["continuous_cum", "continuous_threshold", "continuous_cum_threshold"]

    def __init__(
        self,
        n_lookback: int,
        cum_return: float,
        single_day_return_threshold: float = None,
        pattern_type: str = "continuous_cum",
    ):
        self.n_lookback = n_lookback
        self.cum_return = cum_return
        self.single_day_return_threshold = single_day_return_threshold
        self.pattern_type = pattern_type

    @property
    def look_back_period(self):
        return self.n_lookback

    def _is_continuous_cum(self, period_df):
        open_price = period_df.iloc[0][OPEN_PRICE_COLUMN_NAME]
        close_price = period_df.iloc[-1][CLOSE_PRICE_COLUMN_NAME]
        chg = (close_price - open_price)/open_price
        # continuous rise or continuous drop
        if 0 < self.cum_return <= chg or 0 >= self.cum_return >= chg:
            return True
        return False

    def _is_continuous_threshold(self, period_df):
        # single_day_return_threshold is positive
        if self.single_day_return_threshold > 0:
            if (period_df[DAILY_RETURN_COLUMN_NAME] > self.single_day_return_threshold).sum() == len(period_df):
                return True
        # single_day_return_threshold is negative
        else:
            if (period_df[DAILY_RETURN_COLUMN_NAME] < self.single_day_return_threshold).sum() == len(period_df):
                return True
        return False

    def is_form(self, period_df, cur_pos):
        if self.pattern_type == "continuous_cum":
            return self._is_continuous_cum(period_df)
        elif self.pattern_type == "continuous_threshold":
            return self._is_continuous_threshold(period_df)
        elif self.pattern_type == "continuous_cum_threshold":
            if self._is_continuous_cum(period_df) and self._is_continuous_threshold(period_df):
                return True
            else:
                return False
        else:
            raise NotImplementedError(f"{self.pattern_type} is not valid, available types are {self.available_types}")
