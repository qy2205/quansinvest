import pandas as pd
from quansinvest.data.constants import (
    ADJ_CLOSE_PRICE_COLUMN_NAME,
    OPEN_PRICE_COLUMN_NAME,
)
from quansinvest.evaluation.metrics.base import BaseMetrics


class MaxLoss(BaseMetrics):
    name = "MaxLoss"

    def __call__(
        self,
        data,
        price_col=ADJ_CLOSE_PRICE_COLUMN_NAME,
        min_date: str = None,
        max_date: str = None,
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
            max_loss = None
        else:
            open_price = filtered_data.iloc[0][price_col]
            max_loss = (filtered_data[price_col].min() - open_price)/open_price

        return max_loss
