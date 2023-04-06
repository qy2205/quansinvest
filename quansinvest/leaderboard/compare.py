from collections import defaultdict
from yahoo_fin import stock_info as si
import datetime as dt
import numpy as np
import pandas as pd


def compare_stocks(selected_stocks_df, income_df):
    candidates_df = pd.concat([
        selected_stocks_df,
        selected_stocks_df["Symbol"].apply(lambda x: pd.Series(get_stock_financial(income_df, x)))
    ], axis=1)
    return candidates_df.reset_index(drop=True)


def get_stock_financial(income_df, symbol):
    res = defaultdict(int)
    _income = income_df[income_df["symbol"] == symbol].sort_values(by="date").iloc[-8:]

    if len(_income) == 0:
        return {}

    res["Select"] = np.nan
    res["Price"] = si.get_data(symbol, start_date = dt.datetime.now().date() - dt.timedelta(5)).iloc[-1]["adjclose"]
    res["EPS"] = _income.rolling(4)["EPS (Diluted)"].sum().iloc[-1]
    res["EPS_Guidence"] = np.nan
    res["EPS%Chg"] = np.nan
    res["PE"] = res["price"]/res["EPS"]

    res["Dividends"] = _income["Dividend Per Share"].iloc[-1]*4
    res["Dividends_Ratio"] = res["Dividends"]/res["Price"]
    res["Dividend_Growth"] = _income["Dividend Growth"].median()

    res["Revenue"] = _income.rolling(4)["Revenue"].sum().iloc[-1]
    res["Revenue_Guidence"] = np.nan
    res["Revenue%Chg"] = np.nan

    res["Forward Repurchase"] = np.nan
    res["Recent Repurchase"] = _income["Shares Outstanding (Basic)"].diff().mean()

    res["Revenue_Growth"] = _income["Revenue Growth (YoY)"].median()

    res["Gross_Margin"] = _income["Gross Margin"].median()
    res["Operating_Margin"] = _income["Operating Margin"].median()
    res["Profit_Margin"] = _income["Profit Margin"].median()

    res["Free_Cash_Flow_Per_Share"] = _income["Free Cash Flow Per Share"].median()

    res["Notes"] = np.nan

    return res
