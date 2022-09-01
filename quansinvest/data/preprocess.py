import pandas as pd

from quansinvest.data.constants import (
    MARKET_DATA_COLUMNS,
    DAILY_RETURN_COLUMN_NAME,
    ADJ_CLOSE_PRICE_COLUMN_NAME,
)


def format_data(
    df: pd.DataFrame,
    ohlcvt: list = MARKET_DATA_COLUMNS,
    date_column: str = "index",
    fillna: bool = True,
    drop_duplicates: bool = True,
):
    """The expected dataframe has columns = MARKET_DATA_COLUMNS with date index
    :param df: input dataframe
    :param ohlcvt: open, high, low, close, volume and ticker column names
    :param date_column: date column name, if index, then df.index is date
    :param fillna: True or False
    :param drop_duplicates: True or False
    :return: formatted data
    """
    if date_column != "index":
        df.index = df[date_column]
        del df[date_column]

    # change the data type to datetime
    df.index = pd.to_datetime(df.index.values)

    # rename columns
    for i, col in enumerate(ohlcvt):
        if not col:
            ohlcvt[i] = MARKET_DATA_COLUMNS[i]
    df = df.rename(columns=dict(zip(ohlcvt, MARKET_DATA_COLUMNS)))

    # sort df based on date in ascending order
    # the first row is the earliest date and last row is the latest date
    df = df.sort_index(ascending=True)

    # dropna in date index
    df = df[df.index.notnull()]

    # fillna
    if fillna:
        df = df.fillna(method="ffill")

    # drop duplicates
    if drop_duplicates:
        df = df[~df.index.duplicated(keep='last')]

    # add daily return
    df[DAILY_RETURN_COLUMN_NAME] = (df[ADJ_CLOSE_PRICE_COLUMN_NAME] - df[ADJ_CLOSE_PRICE_COLUMN_NAME].shift(1)) / df[
        ADJ_CLOSE_PRICE_COLUMN_NAME].shift(1)
    df[DAILY_RETURN_COLUMN_NAME] = df[DAILY_RETURN_COLUMN_NAME].fillna(0)

    return df


def resample_to_day_freq(df):
    return df.reindex(
        pd.date_range(
            start=df.index.min(),
            end=df.index.max(),
            freq='D'
        ),
        method='ffill',
    )
