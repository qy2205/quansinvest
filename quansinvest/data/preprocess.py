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
    fillna: bool = False,
    drop_duplicates: bool = False,
    add_daily_return: bool = True,
):
    """The expected dataframe has columns = MARKET_DATA_COLUMNS with date index
    :param df: input dataframe
    :param ohlcvt: open, high, low, close, volume and ticker column names
    :param date_column: date column name, if index, then df.index is date
    :param fillna: True or False
    :param drop_duplicates: True or False
    :param add_daily_return: True or False
    :return: formatted data
    """
    data = df.copy()

    if date_column != "index":
        data.index = data[date_column]
        del data[date_column]

    # change the data type to datetime
    data.index = pd.to_datetime(data.index.values)

    # rename columns
    for i, col in enumerate(ohlcvt):
        if not col:
            ohlcvt[i] = MARKET_DATA_COLUMNS[i]
    data = data.rename(columns=dict(zip(ohlcvt, MARKET_DATA_COLUMNS)))

    # sort df based on date in ascending order
    # the first row is the earliest date and last row is the latest date
    data = data.sort_index(ascending=True)

    # dropna in date index
    data = data[data.index.notnull()]

    # fillna
    if fillna:
        data = data.fillna(method="ffill")

    # drop duplicates
    if drop_duplicates:
        data = data[~data.index.duplicated(keep='last')]

    # add daily return
    if add_daily_return:
        data[DAILY_RETURN_COLUMN_NAME] = (data[ADJ_CLOSE_PRICE_COLUMN_NAME] - data[ADJ_CLOSE_PRICE_COLUMN_NAME].shift(1)) / data[
            ADJ_CLOSE_PRICE_COLUMN_NAME].shift(1)
        data[DAILY_RETURN_COLUMN_NAME] = data[DAILY_RETURN_COLUMN_NAME].fillna(0)

    return data


def resample_to_day_freq(df):
    return df.reindex(
        pd.date_range(
            start=df.index.min(),
            end=df.index.max(),
            freq='D'
        ),
        method='ffill',
    )
