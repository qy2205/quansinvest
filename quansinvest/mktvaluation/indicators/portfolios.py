from quansinvest.mktvaluation.indicators.base import AbstractIndicator
from quansinvest.data.preprocess import format_data
from quansinvest.data.constants import (
    TICKER_COLUMN_NAME,
    VOLUME_COLUMN_NAME,
)
import yahoo_fin.stock_info as si


class PortfolioData(AbstractIndicator):
    available_names = [
        "all_weather",
        "golden_butterfly",
        "harry_browne",
        "warren_buffett",
        "information_technology",
        "consumer_discretionary",
        "healthcare",
        "financials",
        "industrials",
        "utilities",
        "consumer_staples",
        "materials",
        "real_estate",
        "communication_services",
        "energy",
        "preferred_stock",
    ]

    _symbols = [
        ["VTI", "TLT", "IEI", "GLD", "GSG"],
        ["IJS", "VTI", "SHY", "TLT", "GLD"],
        ["VTI", "TLT", "BIL", "GLD"],
        ["BRK-B"],
        ["XLK"],
        ["XLY"],
        ["XLV"],
        ["XLF"],
        ["XLI"],
        ["XLU"],
        ["XLP"],
        ["XLB"],
        ["XLRE"],
        ["XLC"],
        ["XLE"],
        ["PFF"],
    ]

    weights = [
        [0.3, 0.4, 0.15, 0.075, 0.075],
        [0.2, 0.2, 0.2, 0.2, 0.2],
        [0.25, 0.25, 0.25, 0.25],
        [1],
        [1],
        [1],
        [1],
        [1],
        [1],
        [1],
        [1],
        [1],
        [1],
        [1],
        [1],
        [1],
    ]

    names_weights_map = dict(zip(available_names, weights))

    def _get_data(self, name="all_weather"):
        # initialization
        data = si.get_data(PortfolioData.names_symbols_map[name][0])
        data = format_data(data, add_daily_return=False)
        del data[TICKER_COLUMN_NAME], data[VOLUME_COLUMN_NAME]
        data = data*PortfolioData.names_weights_map[name][0]/data.iloc[0]

        for symbol, weight in zip(
            PortfolioData.names_symbols_map[name][1:], PortfolioData.names_weights_map[name][1:]
        ):
            df = si.get_data(symbol)
            df = format_data(df, add_daily_return=False)
            del df[TICKER_COLUMN_NAME], df[VOLUME_COLUMN_NAME]
            data += df * weight / df.iloc[0]

        data[TICKER_COLUMN_NAME] = name
        data = format_data(data)
        data = data.dropna()

        return data


if __name__ == "__main__":
    AllWeather = PortfolioData(name="all_weather")
