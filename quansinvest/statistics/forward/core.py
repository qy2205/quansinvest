from quansinvest.statistics.forward.forms.abstract import AbstractForm
import pandas as pd
from quansinvest.data.constants import (
    CLOSE_PRICE_COLUMN_NAME,
    HIGH_PRICE_COLUMN_NAME,
    LOW_PRICE_COLUMN_NAME,
)


class ForwardLookStatistics:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def _forward_statistics(self, cur_pos, forward_look_period):
        # open position using current date's close price
        open_price = self.data.iloc[cur_pos][CLOSE_PRICE_COLUMN_NAME]
        # close position using the close price after the forward period
        close_price = self.data.iloc[cur_pos + forward_look_period + 1][CLOSE_PRICE_COLUMN_NAME]
        # highest price
        high_price = self.data.iloc[(cur_pos + 1): (cur_pos + forward_look_period + 1)][HIGH_PRICE_COLUMN_NAME]
        # lowest price
        low_price = self.data.iloc[(cur_pos + 1): (cur_pos + forward_look_period + 1)][LOW_PRICE_COLUMN_NAME]

        # statistics
        period_return = (close_price - open_price) / open_price
        max_return = (high_price - open_price) / open_price
        max_drawdown = (low_price - open_price) / open_price

        return {
            "period_return": period_return,
            "max_return": max_return,
            "max_drawdown": max_drawdown,
        }

    def get_results(self, form: AbstractForm, forward_look_period: int) -> list[(pd.DataFrame, dict)]:
        # TODO: parallelize this for loop
        results = []
        start_pos = form.look_back_period
        end_pos = len(self.data) - forward_look_period
        for cur_pos in range(start_pos, end_pos):
            if form.is_form(self.data, cur_pos):
                # period df + forward looking df
                return_df = self.data.iloc[(cur_pos - start_pos): (cur_pos + forward_look_period + 1)]

                # calculate statistics
                statistics_dict = self._forward_statistics(cur_pos, forward_look_period)

                # add to the collected_period_dfs
                results.append((return_df, statistics_dict))
        return results
