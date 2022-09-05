import pandas as pd

from quansinvest.evaluation.metrics.annual_return import AnnualReturn
from quansinvest.evaluation.metrics.sharpe_ratio import SharpeRatio
from quansinvest.data.preprocess import format_data
from quansinvest.evaluation.asset_evaluation import evaluate_asset
from quansinvest.data.constants import TICKER_COLUMN_NAME


def rank(
    symbols,
    start_date: str,
    end_date: str,
    alldata: pd.DataFrame = None,
    freq: str = "D",
    metrics: tuple = (AnnualReturn(), SharpeRatio()),
    timeframe: tuple = ("3M", "6M", "1Y", "2Y", "3Y", "4Y", "5Y", "10Y", "15Y", "20Y", "25Y"),
    use_database: bool = False,
    database_engine=None,
):
    results = []
    for asset_name in symbols:
        if use_database:
            # get ETF data
            data = pd.read_sql_query(
                f"""
                select 
                    * 
                from etf 
                    where symbol = '{asset_name}' and date <= '{end_date}' and date >= '{start_date}'
                """, con=database_engine)
            data = format_data(
                data,
                ohlcvt=["open", "high", "low", "adj_close", "volume", "symbol"],
                date_column="date",
                fillna=True,
                drop_duplicates=True,
            )
        else:
            data = alldata[alldata[TICKER_COLUMN_NAME] == asset_name]
            data = format_data(
                data,
                fillna=False,
                drop_duplicates=False,
            )
            data = data[(data.index <= end_date) & (data.index >= start_date)]

        res = evaluate_asset(
            data,
            freq=freq,
            metrics=metrics,
            timeframe=timeframe,
        )

        res["asset"] = asset_name
        res["launch_date"] = min(data.index)
        res["end_date"] = max(data.index)
        results.append(res)

    return pd.DataFrame(results)
