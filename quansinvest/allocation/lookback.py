import pandas as pd
from quansinvest.leaderboard.rank import fastrank
from quansinvest.evaluation.metrics.annual_return import AnnualReturn
from quansinvest.evaluation.metrics.sharpe_ratio import SharpeRatio
from quansinvest.evaluation.metrics.maxdrawdown import MaxDrawDown
from quansinvest.evaluation.metrics.period_return import PeriodReturn
from quansinvest.utils.utils import etf_name_map, etf_asset_class_map

import matplotlib.pyplot as plt
import seaborn as sns


def get_best_assets(
    data,
    periods,
    freq: str = "D",
    metrics: tuple = (AnnualReturn(), SharpeRatio(), MaxDrawDown(), PeriodReturn()),
    timeframe: tuple = ("100Y",),
    benchmark="SPY",
):
    # rank assets
    topdf_ls = []
    rank_dfs = []

    for start_date, end_date in periods.items():
        stock_ls = data[data.index <= start_date].ticker.unique()
        if len(stock_ls) == 0:
            continue
        rank_df = fastrank(
            symbols=stock_ls,
            alldata=data,
            start_date=start_date,
            end_date=end_date,
            freq=freq,
            metrics=metrics,
            timeframe=timeframe,
            benchmark=benchmark,
        )

        # format rankdf
        period_length = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days
        topdf = rank_df.sort_values(
            by=f"SharpeRatio_100Y", ascending=False
        )[["asset", "launch_date", f"AnnualReturn_100Y", f"SharpeRatio_100Y",
           "MaxDrawDown", "PeriodReturn", f"PeriodReturn_vs_{benchmark}", f"MaxDrawDown_vs_{benchmark}"]]
        topdf.columns = ["asset", "launch_date", "AnnualReturn", "SharpeRatio", "MaxDrawDown",
                         "PeriodReturn", f"PeriodReturn_vs_{benchmark}", f"MaxDrawDown_vs_{benchmark}"]

        # add period length
        topdf["PeriodLen"] = period_length
        rank_df["PeriodLen"] = period_length

        # add period
        topdf["Period"] = [(start_date, end_date)]*len(topdf)
        rank_df["Period"] = [(start_date, end_date)]*len(rank_df)

        topdf_ls.append(topdf)
        rank_dfs.append(rank_df)

    joined_topdf = pd.concat(topdf_ls)
    best_assets = joined_topdf.groupby("asset").agg(
        {
            "asset": "count",
            "AnnualReturn": ["mean", "max", "min"],
            "SharpeRatio": ["mean", "max", "min"],
            "MaxDrawDown": ["mean", "max", "min", lambda x: list(x)],
            "PeriodReturn": ["mean", "max", "min", lambda x: list(x)],
            "PeriodLen": "mean",
            "Period": lambda x: list(x),
            f"PeriodReturn_vs_{benchmark}": lambda x: list(x),
            f"MaxDrawDown_vs_{benchmark}": lambda x: list(x),
        }
    ).sort_values(by=[('asset', 'count'), ("SharpeRatio", "mean")], ascending=[False, False])
    best_assets["win_rate"] = best_assets[('PeriodReturn', '<lambda_0>')].map(
        lambda x: sum([i > 0 for i in x]) / len(x)
    )
    best_assets["return/risk"] = - best_assets[("PeriodReturn", "mean")] / best_assets[("MaxDrawDown", "mean")]
    best_assets["benchmark_score"] = best_assets[(f"MaxDrawDown_vs_{benchmark}", "<lambda>")].map(
        lambda x: sum([i > 0 for i in x])
    ) + best_assets[(f"PeriodReturn_vs_{benchmark}", "<lambda>")].map(
        lambda x: sum([i > 0 for i in x])
    )

    # drop columns index level
    best_assets.columns = ['_'.join(col) if col[1] else col[0] for col in best_assets.columns]

    # add name and asset class
    best_assets["name"] = best_assets.index.map(lambda x: etf_name_map(x))
    best_assets["asset_class"] = best_assets.index.map(lambda x: etf_asset_class_map(x))
    return best_assets, rank_dfs


def get_asset_performance(result, asset="XLU", benchmark="SPY"):
    period_returns = result[result.index == asset]["PeriodReturn_<lambda_0>"].iloc[0]
    max_drawdowns = result[result.index == asset]['MaxDrawDown_<lambda_0>'].iloc[0]
    periods = result[result.index == asset]["Period_<lambda>"].iloc[0]
    period_returns_v_bch = result[result.index == asset][f"PeriodReturn_vs_{benchmark}_<lambda>"].iloc[0]
    max_drawdowns_v_bch = result[result.index == asset][f"MaxDrawDown_vs_{benchmark}_<lambda>"].iloc[0]
    return pd.DataFrame({
        "periods": periods,
        f"{asset}_period_returns": period_returns,
        f"{asset}_max_drawdowns": max_drawdowns,
        f"period_returns_vs_{benchmark}": period_returns_v_bch,
        f"max_drawdowns_vs_{benchmark}": max_drawdowns_v_bch,
    })


def visualize_sensitivity_results(sensitivity_results, symbol="INTU", visual=True, remove_periods=None):
    """
    :param sensitivity_results: from out of sample analysis
    :param symbol:
    :param visual:
    :param remove_periods
    :return:
    """
    # get original periods
    original_periods = get_asset_performance(
        sensitivity_results["start0_end0"].loc["train_raw_results"].iloc[-1],
        symbol
    )["periods"].values

    period_res_dfs = []
    for time_period, res in sensitivity_results.items():
        start_adj, end_adj = time_period.split("_")
        start_adj = int(start_adj.split("start")[-1])
        end_adj = int(end_adj.split("end")[-1])
        period_res = get_asset_performance(res.loc["train_raw_results"].iloc[-1], symbol)
        period_res["start_adj"] = start_adj
        period_res["end_adj"] = end_adj
        period_res["original_periods"] = original_periods[:len(period_res)]

        # remove some periods
        if remove_periods is not None:
            period_res = period_res[period_res["original_periods"].map(lambda x: x[0] not in remove_periods)]

        period_res_dfs.append(period_res)

    period_res_df = pd.concat(period_res_dfs)

    # buy time adj and sell time adj summary
    start_adj_summary = period_res_df.groupby("start_adj")[
        [f"{symbol}_period_returns", f"{symbol}_max_drawdowns"]
    ].describe()
    end_adj_summary = period_res_df.groupby("end_adj")[
        [f"{symbol}_period_returns", f"{symbol}_max_drawdowns"]
    ].describe()

    def visualize_return_drawdown(data, x_name):
        plt.figure(figsize=(16, 6))
        graph = sns.scatterplot(
            data=data,
            x=x_name,
            y=f"{symbol}_period_returns",
            hue="original_periods",
            # marker="+",
            s=75,
        )
        graph.axhline(0, color="red", linestyle="--")
        graph.axhline(0.1, color="green", linestyle="--")
        graph.axhline(0.2, color="green", linestyle="--")

        drawdown_graph = sns.scatterplot(
            data=data,
            x=x_name,
            y=f"{symbol}_max_drawdowns",
            hue="original_periods",
            marker="*",
            s=200,
            legend=False,
        )
        drawdown_graph.axhline(-0.1, color="red", linestyle="--")
        drawdown_graph.axhline(-0.2, color="red", linestyle="--")

        plt.show()

    if visual:
        start_adj_res = period_res_df[period_res_df["end_adj"] == 0]
        end_adj_res = period_res_df[period_res_df["start_adj"] == 0]
        visualize_return_drawdown(start_adj_res, "start_adj")
        visualize_return_drawdown(end_adj_res, "end_adj")

    return period_res_df, start_adj_summary, end_adj_summary
