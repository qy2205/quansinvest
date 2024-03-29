import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt
import numpy as np


def scrapy_fedfund_target_rate(url='https://www.federalreserve.gov/monetarypolicy/openmarket.htm'):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    result = requests.get(url, headers=headers)

    soup = BeautifulSoup(result.content)
    tables = soup.select("table")

    years = soup.select("h4")
    remove_idx = []
    for i, year in enumerate(years):
        if len(year.text) != 4:
            remove_idx.append(i)

    for idx in remove_idx:
        years.pop(idx)

    dfs = []
    for year, table in zip(years, tables):
        df = pd.read_html(str(table))[0]
        df["Date"] = df["Date"].map(lambda x: pd.to_datetime(x + " " + year.text))
        dfs.append(df)
    data = pd.concat(dfs)
    data["Increase"] = data["Increase"].replace({"...": 0}).map(int)
    data["Decrease"] = data["Decrease"].replace({"...": 0, "75-100": 100}).map(int)

    data["Lower"] = data["Level (%)"].map(
        lambda x: float(x.split("-")[0]) if isinstance(x, str) and len(x.split("-")) == 2 else x).map(float)
    data["Upper"] = data["Level (%)"].map(
        lambda x: float(x.split("-")[1]) if isinstance(x, str) and len(x.split("-")) == 2 else x).map(float)
    return data


def get_fedfund_target_data():
    df1 = scrapy_fedfund_target_rate()
    df2 = scrapy_fedfund_target_rate("https://www.federalreserve.gov/monetarypolicy/openmarket_archive.htm")
    data = pd.concat([df1, df2])
    data["open"] = data["Upper"]
    data["high"] = data["Upper"]
    data["low"] = data["Upper"]
    data["close"] = data["Upper"]
    data["adjclose"] = data["Upper"]
    data["volume"] = data["Upper"]
    data["ticker"] = "FedTarget"
    data.index = data["Date"].map(pd.to_datetime)
    return data[["open", "high", "low", "close", "adjclose", "volume", "ticker"]]


def find_fed_periods():
    df1 = scrapy_fedfund_target_rate()
    df2 = scrapy_fedfund_target_rate("https://www.federalreserve.gov/monetarypolicy/openmarket_archive.htm")
    data = pd.concat([df1, df2])
    data["date_diff"] = (data["Date"] - data.shift(-1)["Date"]).map(lambda x: x.days if x else 0)

    p0 = 0
    p1 = 1

    increase_period = []
    increase_fastly_period = []
    increase_slowly_period = []
    decrease_period = []
    decrease_fastly_period = []
    decrease_slowly_period = []
    keep_rate_after_increase_period = []
    keep_rate_after_decrease_period = []

    while p1 < len(data):
        # if p1 in the period
        if data.iloc[p1]["date_diff"] < 120:
            p1 += 1
        # if p1 in the end of period
        else:
            # skip if only 1 raise/decrease
            if p0 == p1:
                p0 += 1
                p1 += 1
                continue
            else:
                # record this period
                period = (str(data.iloc[p1]["Date"])[:10], str(data.iloc[p0]["Date"])[:10])
                # record the pause period
                pause_period = None
                if p1 + 1 <= len(data) - 1:
                    pause_period = (
                        str(data.iloc[p1 + 1]["Date"] + dt.timedelta(1))[:10],
                        str(data.iloc[p1]["Date"] - dt.timedelta(1))[:10]
                    )
                # increase interest rate
                if data.iloc[p1]["Increase"] > 0:
                    increase_period.append(period)
                    if data.iloc[p0:(p1 + 1)]["Increase"].mean() > 30:
                        increase_fastly_period.append(period)
                    else:
                        increase_slowly_period.append(period)
                    keep_rate_after_decrease_period.append(pause_period)

                # decrease interest rate
                elif data.iloc[p1]["Decrease"] > 0:
                    decrease_period.append(period)
                    if data.iloc[p0:(p1 + 1)]["Decrease"].mean() > 30:
                        decrease_fastly_period.append(period)
                    else:
                        decrease_slowly_period.append(period)
                    keep_rate_after_increase_period.append(pause_period)
                p1 += 1
                p0 = p1
    return {
        "increase_period": dict(increase_period),
        "increase_fastly_period": dict(increase_fastly_period),
        "increase_slowly_period": dict(increase_slowly_period),
        "decrease_period": dict(decrease_period),
        "decrease_fastly_period": dict(decrease_fastly_period),
        "decrease_slowly_period": dict(decrease_slowly_period),
        "keep_rate_after_increase_period": dict(keep_rate_after_increase_period),
        "keep_rate_after_decrease_period": dict(keep_rate_after_decrease_period),
    }


def get_fed_fund_rates(save=False):
    url = "https://markets.newyorkfed.org/read?startDt=2000-01-01&endDt=2023-01-29&eventCodes=510,515,520," \
          "500,505&productCode=50&sort=postDt:-1,eventCode:1&format=xlsx"
    fed_fund_rates = pd.read_excel(url)
    fed_fund_rates = fed_fund_rates[fed_fund_rates["Rate Type"] == "EFFR"][
        ["Effective Date", "Rate (%)", "Target Rate From (%)", "Target Rate To (%)"]
    ]
    fed_fund_rates = fed_fund_rates.reset_index(drop=True)
    fed_fund_rates["Effective Date"] = fed_fund_rates["Effective Date"].map(pd.to_datetime)
    fed_fund_rates["Target Rate To (%)"] = np.where(
        fed_fund_rates["Target Rate To (%)"] == fed_fund_rates["Target Rate To (%)"],
        fed_fund_rates["Target Rate To (%)"],
        fed_fund_rates["Target Rate From (%)"]
    )
    fed_fund_rates = fed_fund_rates.rename(
        {
            "Effective Date": "date",
            "Rate (%)": "rate",
            "Target Rate From (%)": "target_from",
            "Target Rate To (%)": "target_to"
        }, axis=1
    )
    if save:
        fed_fund_rates.to_csv("fedrate.csv", index=False)

    return fed_fund_rates
