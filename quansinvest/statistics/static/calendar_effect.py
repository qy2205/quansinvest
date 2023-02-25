"""
1. Daily, Weekly, Semi-monthly, Monthly and Yearly return of different assets and strategies
2. performance in presidential election and midterm election years
3. Christmas and other holidays
4. weekday performance
"""
from quansinvest.data.constants import DAILY_RETURN_COLUMN_NAME
from quansinvest.utils.utils import get_cmap
from quansinvest.data.preprocess import format_data

from yahoo_fin import stock_info as si
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 300


def get_freq_return(data, freq: str = "month"):
    """
    Get return in different frequency
    :param data:
    :param freq: month, year, week or weekday
    :return:
    """
    def total_return_from_returns(returns):
        return (returns + 1).prod() - 1
    return_series = data[DAILY_RETURN_COLUMN_NAME]
    if freq == "year":
        return return_series.groupby(
            by=lambda x: getattr(x, "year")
        ).apply(total_return_from_returns)
    elif freq in ["week", "weekday"]:
        return return_series.groupby(
            by=lambda x: (getattr(x, "year"), getattr(x.isocalendar(), freq))
        ).apply(total_return_from_returns)
    else:
        return return_series.groupby(
            by=lambda x: (getattr(x, "year"), getattr(x, freq))
        ).apply(total_return_from_returns)


def plot_return_distribution(
    symbol: str,
    freq: str = "month",
    include_last_n: int = 3,
    mark_extreme_values: float = 0.99,
):
    """
    plot return distribution and show where is the current return in the graph
    :param symbol: stock symbol
    :param freq: month, year, week or weekday
    :param include_last_n: include last n points in the graph
    :param mark_extreme_values: show when the extreme returns happened in the past, 0.99 means show returns
    above 99% quantile and returns below 1% quantile
    :return:
    """
    data = si.get_data(symbol)
    data = format_data(data)
    returns = get_freq_return(data, freq=freq)

    # histogram
    returns.hist(bins=min(len(returns) // 5, 100), figsize=(22, 6), alpha=0.2, color="green")

    # plot last n points
    colors = get_cmap(include_last_n + 6)
    last_n_rets = returns.tail(include_last_n)
    for i, (_time, _ret) in enumerate(zip(last_n_rets.index, last_n_rets.values)):
        _time_str = f"{_time[0]}-{_time[1]}"
        plt.plot(_ret, 1, marker="o", color=colors(i), markersize=10, label=f"{_time_str} = {round(_ret * 100, 2)}%")

    # plot mean, median, 95% quantile, 5% quantile
    mean_return = round(returns.mean(), 4)
    median_return = round(returns.median(), 4)
    q095_return = round(returns.quantile(0.95), 4)
    q005_return = round(returns.quantile(0.05), 4)
    q099_return = round(returns.quantile(0.99), 4)
    q001_return = round(returns.quantile(0.01), 4)
    for i, (_value, _name) in enumerate(
            zip(
                [mean_return, median_return, q095_return, q005_return, q099_return, q001_return],
                ["mean", "median", "95% quantile", "5% quantile", "99% quantile", "1% quantile"]
            )
    ):
        plt.axvline(x=_value, color=colors(include_last_n + i), label=f"{_name} = {round(_value * 100, 2)}%")

    # annotation
    if mark_extreme_values:
        # assume mark_extreme_values > 0.5
        high_ret = returns.quantile(mark_extreme_values)
        low_ret = returns.quantile(1 - mark_extreme_values)
        high_ret_str = "\n".join([f"{_time[0]}-{_time[1]}" for _time in returns[returns >= high_ret].index])
        low_ret_str = "\n".join([f"{_time[0]}-{_time[1]}" for _time in returns[returns <= low_ret].index])
        # plot
        plt.annotate(high_ret_str, (high_ret * 1.01, 0.5))
        plt.annotate(low_ret_str, (low_ret * 0.99, 0.5))

    plt.legend()
    plt.show()


def certain_month_effect(symbol: str, month: int = 1):
    """
    will certain month return affect the full year return?
    :param symbol: str, stock symbol
    :param month: int, which month you are interested in
    :return:
    """
    data = si.get_data(symbol)
    data = format_data(data)
    yearly_ret = get_freq_return(data, freq="year")
    monthly_ret = get_freq_return(data, freq="month")
    pairs = []
    for _year, _year_ret in yearly_ret.iteritems():
        try:
            _jan_ret = monthly_ret[(_year, month)]
        except KeyError:
            continue
        pairs.append([_year, _year_ret, _jan_ret])
    result = pd.DataFrame(pairs, columns=["year", "year_return", "m_return"])
    result["year_return>0"] = result["year_return"].map(lambda x: int(x > 0))
    result["m_return>0"] = result["m_return"].map(lambda x: int(x > 0))

    prob = ((result["year_return>0"] == result["m_return>0"]).sum() - 1) / (len(result) - 1)

    print(f"{month} month -> year probability = {round(prob, 4)}")

    return result
