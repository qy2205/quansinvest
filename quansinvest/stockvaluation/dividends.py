from quansinvest.data.financial import scrapy_dividends
import yahoo_fin.stock_info as si
import pandas as pd


def dividends_valuation(symbol):
    df = scrapy_dividends(symbol)
    df.index = pd.to_datetime(df["Ex-Dividend Date"]).values
    df["dividends"] = df["Cash Amount"].map(lambda x: float(x[1:]))
    df = df[["dividends"]]
    df = df.sort_index()
    dividends_df = pd.merge_asof(df, si.get_data(symbol)[["adjclose", "close"]], left_index=True, right_index=True)
    dividends_df["dividends_TTM"] = dividends_df["dividends"].rolling(4).sum()
    dividends_df["dividends_ratio"] = dividends_df["dividends_TTM"] / dividends_df["close"]
    return dividends_df
