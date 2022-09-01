import pandas as pd
from .base import AbstractIndicator
from quansinvest.data.preprocess import format_data
import yahoo_fin.stock_info as si


class USTreasuryRate(AbstractIndicator):
    def get_data(self, name="30Y"):
        # US 30Y Treasury Rate
        if name == "30Y":
            data = si.get_data("^TYX")
            data = format_data(data)
            return data
        elif name == "13W":
            data = si.get_data("^IRX")
            data = format_data(data)
            return data
        elif name == "5Y":
            data = si.get_data("^FVX")
            data = format_data(data)
            return data
        elif name == "10Y":
            data = si.get_data("^TNX")
            data = format_data(data)
            return data
        return pd.DataFrame()
