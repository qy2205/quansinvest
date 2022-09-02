from .base import AbstractIndicator
from quansinvest.data.preprocess import format_data
import yahoo_fin.stock_info as si


class Commodities(AbstractIndicator):
    available_names = [
        # energy
        "brent_oil", "oil", "gas", "heating_oil",
        # metal
        "gold", "copper", "aluminum", "silver",
        # food
        "wheat", "corn", "soybean", "sugar", "cotton", "orange_juice", "coffee", "cocoa", "oat", "rough_rice",
        # meat
        "feeder_cattle", "live_cattle", "lean_hogs",
        # wood
        "lumber",
    ]

    _symbols = [
        # energy
        "BZ=F", "CL=F", "NG=F", "HO=F",
        # metal
        "^HUI", "HG=F", "ALI=F", "SI=F",
        # food
        "KE=F", "ZC=F", "ZS=F", "SB=F", "CT=F", "OJ=F", "KC=F", "CC=F", "ZO=F", "ZR=F",
        # meat
        "GF=F", "LE=F", "HE=F",
        # wood
        "LBS=F",
    ]

    def _get_data(self, name="brent_oil"):
        # Commodities data
        data = si.get_data(Commodities.names_symbols_map)
        data = format_data(data)
        return data
