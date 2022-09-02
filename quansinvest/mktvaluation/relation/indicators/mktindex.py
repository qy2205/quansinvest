import numpy as np
from .base import AbstractIndicator
from quansinvest.data.preprocess import format_data
from quansinvest.data.constants import (
    OPEN_PRICE_COLUMN_NAME,
    ADJ_CLOSE_PRICE_COLUMN_NAME,
)
import yahoo_fin.stock_info as si


class USIndex(AbstractIndicator):
    available_names = [
        "SP500",
        "NASDAQ100",
    ]

    _symbols = [
        "^GSPC",
        "^IXIC"
    ]

    def _get_data(self, name="SP500"):
        data = si.get_data(USIndex.names_symbols_map[name])
        data = format_data(data)

        # SP500 Index
        if name == "SP500":
            # fix GSPC open price = 0 issue
            data[OPEN_PRICE_COLUMN_NAME] = np.where(
                data[OPEN_PRICE_COLUMN_NAME] == 0,
                data[ADJ_CLOSE_PRICE_COLUMN_NAME].shift(1).fillna(method="bfill"),
                data[OPEN_PRICE_COLUMN_NAME])

        return data
