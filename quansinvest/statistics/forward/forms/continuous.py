from .abstract import AbstractForm
from quansinvest.data.constants import (
    CLOSE_PRICE_COLUMN_NAME,
    OPEN_PRICE_COLUMN_NAME,
    DAILY_RETURN_COLUMN_NAME,
)


class ContinuousForm(AbstractForm):
    def __init__(
        self,
        n_lookback: int,
        cum_return: float,
        single_day_return_threshold: float = None,
        form_type: str = "continuous_cum",
    ):
        self.n_lookback = n_lookback
        self.cum_return = cum_return
        self.single_day_return_threshold = single_day_return_threshold
        self.form_type = form_type

    @property
    def available_types(self):
        return ["continuous_cum", "continuous_threshold"]

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
            if (period_df[DAILY_RETURN_COLUMN_NAME] > self.single_day_return_threshold).sum() == period_df.size:
                return True
        # single_day_return_threshold is negative
        else:
            if (period_df[DAILY_RETURN_COLUMN_NAME] < self.single_day_return_threshold).sum() == period_df.size:
                return True
        return False

    def is_form(self, df, cur_pos):
        period_df = df.iloc[(cur_pos - self.n_lookback + 1): (cur_pos + 1)]
        if self.form_type == "continuous_cum":
            return self._is_continuous_cum(period_df)
        elif self.form_type == "continuous_threshold":
            return self._is_continuous_threshold(period_df)
        else:
            raise NotImplementedError(f"{self.form_type} is not valid, available types are {self.available_types}")
