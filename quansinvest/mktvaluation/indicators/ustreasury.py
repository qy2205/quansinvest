from .base import AbstractIndicator
from quansinvest.data.preprocess import format_data
from quansinvest.data.fedfund import get_fedfund_target_data
import yahoo_fin.stock_info as si


class USTreasuryRate(AbstractIndicator):
    available_names = [
        "30Y",
        "13W",
        "5Y",
        "10Y",
        "fed_target",
    ]

    _symbols = [
        "^TYX",
        "^IRX",
        "^FVX",
        "^TNX",
        "",
    ]

    def _get_data(self, name="30Y"):
        # get fed fund target rate from scarpy
        if name == "fed_target":
            data = get_fedfund_target_data()
        else:
            # get US Treasury Rate data from API
            data = si.get_data(USTreasuryRate.names_symbols_map[name])
        data = format_data(data)
        return data
