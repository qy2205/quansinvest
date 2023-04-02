import pandas as pd
import numpy as np
from pandarallel import pandarallel

from quansinvest.evaluation.metrics import (
    AnnualReturn,
    SharpeRatio,
    MaxDrawDown,
    PeriodReturn
)
from quansinvest.data.preprocess import format_data
from quansinvest.evaluation.asset_evaluation import evaluate_asset
from quansinvest.data.constants import TICKER_COLUMN_NAME
from quansinvest.utils.utils import etf_name_map, etf_asset_class_map


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
    # TODO: multiprocessing
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

        # TODO: handle ETF rename
        if len(data) == 0:
            continue

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


def fastrank(
    symbols,
    start_date: str,
    end_date: str,
    alldata: pd.DataFrame,
    freq: str = "D",
    metrics: tuple = (AnnualReturn(), SharpeRatio(), MaxDrawDown(), PeriodReturn()),
    timeframe: tuple = ("3M", "6M", "1Y", "2Y", "3Y", "4Y", "5Y", "10Y", "15Y", "20Y", "25Y"),
    benchmark: str = "SPY",
    # pandarallel parameters
    progress_bar: bool = False,
    verbose=0,
):
    # empty results
    empty_res = {}
    for period in timeframe:
        for metric in metrics:
            if metric.name in ["PeriodReturn", "MaxDrawDown"]:
                empty_res[f"{metric.name}"] = np.nan
            else:
                empty_res[f"{metric.name}_{period}"] = np.nan
    empty_res["asset"] = np.nan
    empty_res["launch_date"] = np.nan
    empty_res["end_date"] = np.nan

    def evaluate(df, benchmark_result=None):
        df = format_data(
            df,
            fillna=False,
            drop_duplicates=False,
        )

        if len(df) == 0:
            return empty_res
        else:
            result = evaluate_asset(
                df,
                freq=freq,
                metrics=metrics,
                timeframe=timeframe,
            )
            result["asset"] = df[TICKER_COLUMN_NAME].iloc[0]
            result["launch_date"] = min(df.index)
            result["end_date"] = max(df.index)
            if benchmark_result:
                result[f"PeriodReturn_vs_{benchmark}"] = (
                        result["PeriodReturn"] - benchmark_result["PeriodReturn"]
                )
                result[f"MaxDrawDown_vs_{benchmark}"] = (
                        result["MaxDrawDown"] - benchmark_result["MaxDrawDown"]
                )
            return result

    # preprocess data
    alldata = alldata[(alldata.index <= end_date) & (alldata.index >= start_date)]

    # eval benchmark
    benchmark_res = None
    if benchmark:
        benchmark_res = evaluate(alldata[alldata[TICKER_COLUMN_NAME] == benchmark], benchmark_result=None)

    # multiprocessing
    alldata = alldata[alldata[TICKER_COLUMN_NAME].isin(symbols)]
    if len(alldata) > 0:
        pandarallel.initialize(progress_bar=progress_bar, verbose=verbose)
        results = alldata.groupby(TICKER_COLUMN_NAME).parallel_apply(lambda df: evaluate(df, benchmark_res)).tolist()
    else:
        results = [evaluate(alldata, benchmark_res)]

    result = pd.DataFrame(results)

    # add name and asset class
    result["name"] = result["asset"].map(lambda x: etf_name_map(x))
    result["asset_class"] = result["asset"].map(lambda x: etf_asset_class_map(x))

    return result
