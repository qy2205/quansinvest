import pandas as pd
import datetime as dt
from quansinvest.data.constants import (
    ADJ_CLOSE_PRICE_COLUMN_NAME,
)
from quansinvest.evaluation.metrics.base import BaseMetrics


class MaxDrawDown(BaseMetrics):
    name = "MaxDrawDown"

    def __init__(self, in_advance_days: int = None, extend_days: int = None):
        self.in_advance_days = in_advance_days
        self.extend_days = extend_days

    def __call__(
        self,
        data,
        price_col=ADJ_CLOSE_PRICE_COLUMN_NAME,
        min_date: str = None,
        max_date: str = None,
        freq: str = "D",
        return_drawdown_series: bool = False,
        *args,
        **kwargs,
    ):
        """
        :param data: assume data has date as index and ranked in ascending order
        :param return_col:
        :param price_col:
        :param min_date:
        :param max_date:
        :param freq:
        :param return_drawdown_series: True or False, whether to return all drawdown
        :return:
        """
        filtered_data = data.copy()

        if self.in_advance_days:
            min_date -= dt.timedelta(self.in_advance_days)
        if self.extend_days:
            max_date += dt.timedelta(self.extend_days)

        if min_date:
            filtered_data = filtered_data[(filtered_data.index >= pd.to_datetime(min_date))]
        if max_date:
            filtered_data = filtered_data[(filtered_data.index <= pd.to_datetime(max_date))]

        if len(filtered_data) == 0:
            max_drawdown, drawdown_series = None, None
        else:
            # method 1
            # drawdown_series = (
            #     (filtered_data[ADJ_CLOSE_PRICE_COLUMN_NAME] -
            #      filtered_data[ADJ_CLOSE_PRICE_COLUMN_NAME].expanding().max()) /
            #     filtered_data[ADJ_CLOSE_PRICE_COLUMN_NAME].expanding().max()
            # )
            # max_drawdown = drawdown_series.min()

            # method 2
            start_price = filtered_data[ADJ_CLOSE_PRICE_COLUMN_NAME].iloc[0]
            min_price = filtered_data[ADJ_CLOSE_PRICE_COLUMN_NAME].min()
            max_drawdown = (min_price - start_price)/start_price
            drawdown_series = None

        if return_drawdown_series:
            return max_drawdown, drawdown_series
        else:
            return max_drawdown
