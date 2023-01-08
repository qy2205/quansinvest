from collections import defaultdict
import pandas as pd
from quansinvest.leaderboard.rank import fastrank
from quansinvest.evaluation.metrics.annual_return import AnnualReturn
from quansinvest.evaluation.metrics.sharpe_ratio import SharpeRatio
from quansinvest.evaluation.metrics.maxdrawdown import MaxDrawDown
from quansinvest.evaluation.metrics.period_return import PeriodReturn


def get_best_assets(data, periods):
    # rank assets
    topdf_ls = []
    rank_dfs = []
    freqCount = defaultdict(int)

    for start_date, end_date in periods.items():
        stock_ls = data[data.index <= start_date].ticker.unique()
        if len(stock_ls) == 0:
            continue
        for stock in stock_ls:
            freqCount[stock] += 1
        rank_df = fastrank(
            symbols=stock_ls,
            alldata=data,
            start_date=start_date,
            end_date=end_date,
            freq="D",
            metrics=(AnnualReturn(), SharpeRatio(), MaxDrawDown(), PeriodReturn()),
            timeframe=("3M", "6M", "1Y", "2Y", "3Y", "4Y", "5Y", "10Y", "15Y", "20Y"),
        )

        # format rankdf
        period_length = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days
        years = max(1, (period_length // 365) + 1)
        if years > 5:
            years = (years//5 + 1) * 5
        topdf = rank_df[rank_df["PeriodReturn"] > 0].sort_values(
            by=f"SharpeRatio_{years}Y", ascending=False
        )[["asset", "launch_date", f"AnnualReturn_{years}Y", f"SharpeRatio_{years}Y", "MaxDrawDown", "PeriodReturn"]]
        topdf.columns = ["asset", "launch_date", "AnnualReturn", "SharpeRatio", "MaxDrawDown", "PeriodReturn"]

        # add period length
        topdf["PeriodLen"] = period_length
        rank_df["PeriodLen"] = period_length

        # add period
        topdf["Period"] = [(start_date, end_date)]*len(topdf)
        rank_df["Period"] = [(start_date, end_date)]*len(rank_df)

        topdf_ls.append(topdf)
        rank_dfs.append(rank_df)

    joined_topdf = pd.concat(topdf_ls)
    freq_df = pd.DataFrame([freqCount]).T
    freq_df.columns = ["freq"]
    best_assets = joined_topdf.groupby("asset").agg(
        {
            "asset": "count",
            "AnnualReturn": ["mean", "max", "min"],
            "SharpeRatio": ["mean", "max", "min"],
            "MaxDrawDown": ["mean", "max", "min", lambda x: list(x)],
            "PeriodReturn": ["mean", "max", "min", lambda x: list(x)],
            "PeriodLen": "mean",
            "Period": lambda x: list(x),
        }
    ).sort_values(by=[('asset', 'count'), ("SharpeRatio", "mean")], ascending=[False, False])
    best_assets = best_assets.join(freq_df, how="left")
    best_assets["win_rate"] = best_assets[("asset", "count")]/best_assets["freq"]
    best_assets["return/risk"] = - best_assets[("PeriodReturn", "mean")] / best_assets[("MaxDrawDown", "mean")]
    return best_assets, rank_dfs
