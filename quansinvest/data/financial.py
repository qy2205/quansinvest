from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import time
import random

headers_ls = [
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'},
    {'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'},
]


def clean_symbol(symbol):
    symbol = symbol.lower()
    if "-" in symbol:
        symbol = symbol.replace("-", ".")
    return symbol


def request_and_retry(url, headers):
    result = requests.get(url, headers=headers)
    if result.status_code == 200:
        print("Request Succeed!")
    elif result.status_code == 429:
        count = 0
        retry_times = 5
        while count < retry_times and result.status_code == 429:
            print(f"Retrying {count}: {url}")
            headers = random.choice(headers_ls)
            result = requests.get(url, headers=headers)
            count += 1
            if result.status_code == 200:
                print("Request Succeed!")
            else:
                if count == retry_times:
                    continue
                else:
                    time.sleep(45)
    else:
        print("Request Failed: ", result)
    return result


def scrapy_income(symbol):
    symbol = clean_symbol(symbol)
    url = f'https://stockanalysis.com/stocks/{symbol}/financials/?period=quarterly'
    headers = random.choice(headers_ls)
    result = request_and_retry(url, headers)
    soup = BeautifulSoup(result.content)
    df = pd.read_html(str(soup.select("table")[0]))[0]
    return df


def scrapy_balance_sheet(symbol):
    symbol = clean_symbol(symbol)
    url = f'https://stockanalysis.com/stocks/{symbol}/financials/balance-sheet/?period=quarterly'
    headers = random.choice(headers_ls)
    result = request_and_retry(url, headers)
    soup = BeautifulSoup(result.content)
    df = pd.read_html(str(soup.select("table")[0]))[0]
    return df


def scrapy_cash_flow(symbol):
    symbol = clean_symbol(symbol)
    url = f'https://stockanalysis.com/stocks/{symbol}/financials/cash-flow-statement/?period=quarterly'
    headers = random.choice(headers_ls)
    result = request_and_retry(url, headers)
    soup = BeautifulSoup(result.content)
    df = pd.read_html(str(soup.select("table")[0]))[0]
    return df


def scrapy_ratios(symbol):
    symbol = clean_symbol(symbol)
    url = f'https://stockanalysis.com/stocks/{symbol}/financials/ratios/?period=quarterly'
    headers = random.choice(headers_ls)
    result = request_and_retry(url, headers)
    soup = BeautifulSoup(result.content)
    df = pd.read_html(str(soup.select("table")[0]))[0]
    return df


def scrapy_dividends(symbol):
    symbol = symbol.lower()
    url = f'https://stockanalysis.com/stocks/{symbol}/dividend/'
    headers = random.choice(headers_ls)
    result = requests.get(url, headers=headers)
    soup = BeautifulSoup(result.content)
    df = pd.read_html(str(soup.select("table")[0]))[0]
    return df


def process_table(df):
    # first col -> index
    df.index = df.iloc[:, 0].values
    df = df.iloc[:, 1:]

    df = df.T
    # remove last row
    if df.iloc[-1][0] == "Upgrade":
        df = df.iloc[:-1, :]

    df.index = pd.to_datetime(df.index)

    def str2num(s):
        if s == "-":
            return np.nan
        if "%" in s:
            return float(s.split("%")[0]) / 100
        else:
            return float(s)

    df = df.applymap(str2num)
    df = df.reset_index().rename({"index": "date"}, axis=1)
    return df


if __name__ == "__main__":
    test_income = scrapy_income("AAPL")
    test_income = process_table(test_income)

    test_bs = scrapy_balance_sheet("AAPL")
    test_bs = process_table(test_bs)

    test_cashflow = scrapy_cash_flow("AAPL")
    test_cashflow = process_table(test_cashflow)
