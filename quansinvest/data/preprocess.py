import pandas as pd
from quansinvest.data.constants import (
    DATE_COLUMN_NAME,
    MARKET_DATA_COLUMNS,
    DAILY_RETURN_COLUMN_NAME,
    OPEN_PRICE_COLUMN_NAME,
    CLOSE_PRICE_COLUMN_NAME,
)


def format_data(
    df: pd.DataFrame,
    dohlcvt: list = MARKET_DATA_COLUMNS,
    is_index_date: bool = False,
):
    """The expected dataframe has columns = MARKET_DATA_COLUMNS
    :param df: input dataframe
    :param dohlcvt: date, open, high, low, close, volume and ticker column names
    :param is_index_date: True if date in index, else False
    :return: formatted data
    """
    if is_index_date:
        # MARKET_DATA_COLUMNS[0] is date
        df[MARKET_DATA_COLUMNS[0]] = df.index

    # rename columns
    for i, col in enumerate(dohlcvt):
        if not col:
            dohlcvt[i] = MARKET_DATA_COLUMNS[i]
    df = df.rename(columns=dict(zip(dohlcvt, MARKET_DATA_COLUMNS)))

    # change the data type to datetime
    df[DATE_COLUMN_NAME] = pd.to_datetime(df[DATE_COLUMN_NAME])

    # sort df based on the date column in ascending order
    # the first row is the earliest date and last row is the latest date
    df = df.sort_values(by=DATE_COLUMN_NAME, ascending=True)

    # add daily return
    df[DAILY_RETURN_COLUMN_NAME] = (df[CLOSE_PRICE_COLUMN_NAME] - df[OPEN_PRICE_COLUMN_NAME])/df[OPEN_PRICE_COLUMN_NAME]

    return df

