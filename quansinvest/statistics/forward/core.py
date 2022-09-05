from quansinvest.statistics.forward.patterns.base import AbstractPattern
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
        close_price = self.data.iloc[cur_pos + forward_look_period][CLOSE_PRICE_COLUMN_NAME]
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

    def get_results(
        self,
        form: AbstractPattern,
        forward_look_period: int
    ) -> list[(pd.DataFrame, pd.DataFrame, dict)]:
        # TODO: parallelize this for loop
        results = []
        start_pos = form.look_back_period - 1
        end_pos = len(self.data)
        for cur_pos in range(start_pos, end_pos):
            period_df = self.data.iloc[(cur_pos - form.look_back_period + 1): (cur_pos + 1)]
            if form.is_form(period_df, cur_pos):
                # forward-looking df
                return_df = self.data.iloc[(cur_pos + 1): (cur_pos + forward_look_period + 1)]

                # calculate statistics
                if cur_pos + forward_look_period + 1 >= end_pos:
                    statistics_dict = {}
                else:
                    statistics_dict = self._forward_statistics(cur_pos, forward_look_period)

                # add to the collected_period_dfs
                results.append((period_df, return_df, statistics_dict))
        return results

    def get_sequential_results(
        self,
        forms: list[AbstractPattern],
        forward_look_period: int,
    ) -> list[(list[pd.DataFrame], pd.DataFrame, dict)]:
        # TODO: parallelize this for loop
        results = []
        n_forms = len(forms)
        start_pos = sum([form.look_back_period for form in forms]) - 1
        end_pos = len(self.data)
        for cur_pos in range(start_pos, end_pos):
            period_dfs = []

            # match sequential patterns
            not_match = False
            cur_pos2 = cur_pos
            for form in forms[::-1]:
                period_df = self.data.iloc[(cur_pos2 - form.look_back_period + 1): (cur_pos2 + 1)]
                period_dfs.insert(0, period_df)
                if form.is_form(period_df, cur_pos2):
                    cur_pos2 -= form.look_back_period
                else:
                    not_match = True
                    break
            if not_match:
                continue

            # period df + forward looking df
            return_df = self.data.iloc[
                (cur_pos + 1): (cur_pos + forward_look_period + 1)
            ]

            # calculate statistics
            if cur_pos + forward_look_period + 1 >= end_pos:
                statistics_dict = {}
            else:
                statistics_dict = self._forward_statistics(cur_pos, forward_look_period)

            # add to the collected_period_dfs
            results.append((period_dfs, return_df, statistics_dict))
        return results
