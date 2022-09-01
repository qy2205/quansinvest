from quansinvest.statistics.forward.forms.base import AbstractForm
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

    def get_results(
        self,
        form: AbstractForm,
        forward_look_period: int
    ) -> list[(pd.DataFrame, pd.DataFrame, dict)]:
        # TODO: parallelize this for loop
        results = []
        start_pos = form.look_back_period - 1
        end_pos = len(self.data)
        for cur_pos in range(start_pos, end_pos):
            period_df = self.data.iloc[(cur_pos - form.look_back_period + 1): (cur_pos + 1)]
            if form.is_form(period_df, cur_pos):
                # period df + forward looking df
                return_df = self.data.iloc[(cur_pos - form.look_back_period + 1): (cur_pos + forward_look_period + 1)]

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
        forms: list[AbstractForm],
        forward_look_periods: list[int],
    ) -> list[(list[pd.DataFrame], pd.DataFrame, dict)]:
        # TODO: parallelize this for loop
        n_forms = len(forms)
        results = []
        start_pos = forms[0].look_back_period - 1
        end_pos = len(self.data)
        for cur_pos in range(start_pos, end_pos):
            period_dfs = []
            for i, form in enumerate(forms):
                period_df = self.data.iloc[(cur_pos - form.look_back_period + 1): (cur_pos + 1)]
                period_dfs.append(period_df)
                if form.is_form(period_df, cur_pos) and (i + 1) < n_forms:
                    cur_pos += forward_look_periods[i]

            # period df + forward looking df
            return_df = self.data.iloc[
                (cur_pos - forms[-1].look_back_period + 1): (cur_pos + forward_look_periods[-1] + 1)
            ]

            # calculate statistics
            if cur_pos + forward_look_periods[-1] + 1 >= end_pos:
                statistics_dict = {}
            else:
                statistics_dict = self._forward_statistics(cur_pos, forward_look_periods[-1])

            # add to the collected_period_dfs
            results.append((period_dfs, return_df, statistics_dict))
        return results
