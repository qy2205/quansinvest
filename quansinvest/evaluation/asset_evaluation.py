from quansinvest.evaluation.metrics.annual_return import AnnualReturn
from quansinvest.evaluation.metrics.sharpe_ratio import SharpeRatio
from quansinvest.evaluation.metrics.period_return import PeriodReturn
from quansinvest.data.constants import (
    ADJ_CLOSE_PRICE_COLUMN_NAME,
    DAILY_RETURN_COLUMN_NAME,
)
import datetime as dt


def evaluate_asset(
    data,
    freq="D",
    metrics: tuple = (AnnualReturn, SharpeRatio, PeriodReturn),
    timeframe: tuple = ("3M", "6M", "1Y", "2Y", "3Y", "4Y", "5Y", "10Y", "15Y", "20Y", "25Y"),
):
    """
    :param data: formatted data
    :param freq: data frequency
    :param metrics: evaluation.metrics
    :param timeframe: look back time period
    :return:
    """
    if len(data) == 0 or len(metrics) == 0 or len(timeframe) == 0:
        return None

    min_date = min(data.index)
    max_date = max(data.index)

    time_dict = {}
    for period in timeframe:
        if period.endswith("M"):
            n_months = float(period.split("M")[0])
            timestamp = min(max_date, min_date + dt.timedelta((365*n_months) // 12))
        elif period.endswith("Y"):
            n_years = float(period.split("Y")[0])
            timestamp = min(max_date, min_date + dt.timedelta(int(365 * n_years)))
        elif period.endswith("W"):
            n_weeks = float(period.split("W")[0])
            timestamp = min(max_date, min_date + dt.timedelta((365*n_weeks) // 52))
        else:
            continue
        time_dict[period] = timestamp

    eval_results = {}
    # PeriodReturn, not based on frequency
    # Other metrics, based on frequency
    for metric in metrics:
        if metric.name in ["PeriodReturn", "MaxDrawDown"]:
            eval_results[f"{metric.name}"] = metric(
                data,
                min_date=min_date,
                max_date=max_date,
                return_col=DAILY_RETURN_COLUMN_NAME,
                price_col=ADJ_CLOSE_PRICE_COLUMN_NAME,
            )
            continue
        for period in time_dict.keys():
            eval_results[f"{metric.name}_{period}"] = metric(
                data,
                min_date=min_date,
                max_date=time_dict[period],
                return_col=DAILY_RETURN_COLUMN_NAME,
                price_col=ADJ_CLOSE_PRICE_COLUMN_NAME,
                freq=freq,
            )

    return eval_results
