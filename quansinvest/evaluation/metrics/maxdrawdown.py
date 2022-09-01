import pandas as pd
from quansinvest.data.constants import (
    ADJ_CLOSE_PRICE_COLUMN_NAME,
)
from quansinvest.evaluation.metrics.base import BaseMetrics


class MaxDrawDown(BaseMetrics):
    name = "MaxDrawDown"

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
        if min_date:
            filtered_data = filtered_data[(filtered_data.index >= pd.to_datetime(min_date))]
        if max_date:
            filtered_data = filtered_data[(filtered_data.index <= pd.to_datetime(max_date))]

        if len(filtered_data) == 0:
            max_drawdown, drawdown_series = None, None
        else:
            drawdown_series = (
                (filtered_data[ADJ_CLOSE_PRICE_COLUMN_NAME] -
                 filtered_data[ADJ_CLOSE_PRICE_COLUMN_NAME].expanding().max()) /
                filtered_data[ADJ_CLOSE_PRICE_COLUMN_NAME]
            )
            max_drawdown = drawdown_series.min()

        if return_drawdown_series:
            return max_drawdown, drawdown_series
        else:
            return max_drawdown
