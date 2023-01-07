import pandas as pd
from quansinvest.data.constants import (
    ADJ_CLOSE_PRICE_COLUMN_NAME,
)
from quansinvest.evaluation.metrics.base import BaseMetrics


class PeriodReturn(BaseMetrics):
    name = "PeriodReturn"

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
        :param price_col:
        :param min_date:
        :param max_date:
        :return:
        """
        filtered_data = data.copy()
        if min_date:
            filtered_data = filtered_data[(filtered_data.index >= pd.to_datetime(min_date))]
        if max_date:
            filtered_data = filtered_data[(filtered_data.index <= pd.to_datetime(max_date))]

        if len(filtered_data) == 0:
            period_return = None
        else:
            open_close = filtered_data.iloc[[0, -1], :][price_col].values
            period_return = (open_close[1] - open_close[0]) / open_close[0]

        return period_return
