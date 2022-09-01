import pandas as pd
import numpy as np
from quansinvest.data.constants import (
    ADJ_CLOSE_PRICE_COLUMN_NAME,
    DAILY_RETURN_COLUMN_NAME,
)
from quansinvest.evaluation.metrics.base import BaseMetrics


class SharpeRatio(BaseMetrics):
    name = "SharpeRatio"

    def __call__(
        self,
        data,
        return_col=DAILY_RETURN_COLUMN_NAME,
        price_col=ADJ_CLOSE_PRICE_COLUMN_NAME,
        min_date: str = None,
        max_date: str = None,
        freq: str = "D",
        return_annual_return_std: bool = False,
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
        :param return_annual_return_std: True or False, whether to return annualized return and annualized std
        :return:
        """
        filtered_data = data.copy()
        if min_date:
            filtered_data = filtered_data[(filtered_data.index >= pd.to_datetime(min_date))]
        if max_date:
            filtered_data = filtered_data[(filtered_data.index <= pd.to_datetime(max_date))]

        if len(filtered_data) == 0:
            sharpe, annual_return, annual_std = None, None, None
        else:
            open_close = filtered_data.iloc[[0, -1], :][price_col].values
            cum_return = (open_close[1] - open_close[0]) / open_close[0]

            # annualized return and std
            annual_return = (1 + cum_return) ** (SharpeRatio.freq_map[freq] / len(filtered_data)) - 1
            annual_std = filtered_data[return_col].std() * np.sqrt(SharpeRatio.freq_map[freq])

            sharpe = annual_return / annual_std

        if return_annual_return_std:
            return sharpe, annual_return, annual_std
        else:
            return sharpe
