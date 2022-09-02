from .base import AbstractIndicator
from quansinvest.data.preprocess import format_data
import yahoo_fin.stock_info as si


class USTreasuryRate(AbstractIndicator):
    available_names = [
        "30Y",
        "13W",
        "5Y",
        "10Y",
    ]

    _symbols = [
        "^TYX",
        "^IRX",
        "^FVX",
        "^TNX",
    ]

    def _get_data(self, name="30Y"):
        # US Treasury Rate data
        data = si.get_data(USTreasuryRate.names_symbols_map[name])
        data = format_data(data)
        return data
