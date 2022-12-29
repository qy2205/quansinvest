from bs4 import BeautifulSoup
import requests
import pandas as pd


def scrapy_financial(symbol):
    symbol = symbol.lower()
    url = f'https://stockanalysis.com/stocks/{symbol}/financials/?period=quarterly'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    result = requests.get(url, headers=headers)
    soup = BeautifulSoup(result.content)
    df = pd.read_html(str(soup.select("table")[0]))[0]
    return df


def scrapy_dividends(symbol):
    symbol = symbol.lower()
    url = f'https://stockanalysis.com/stocks/{symbol}/dividend/'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    result = requests.get(url, headers=headers)
    soup = BeautifulSoup(result.content)
    df = pd.read_html(str(soup.select("table")[0]))[0]
    return df
