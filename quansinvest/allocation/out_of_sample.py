import numpy as np
import pandas as pd
from quansinvest.allocation.lookback import get_best_assets
from quansinvest.allocation.lookback import get_asset_performance


def stock_scoring(df):
    scores = (df["PeriodReturn_<lambda_0>"].map(lambda x: min(0.4, np.median(x))) /
              df["MaxDrawDown_<lambda_0>"].map(lambda x: max(0.1, -np.median(x)))).map(
        lambda x: x * 100 / 4).sort_values(ascending=False)
    return scores


def out_of_sample_analysis(
    alldata,
    periods,
    n_select,
    test_range,
    drawdown_thld,
    drawdown_tol,
    scoring_fun=stock_scoring,
):
    periods = sorted(list(periods.items()), key=lambda x: x[0])

    res = {}

    for i in range(len(periods)):
        train_periods = dict(periods[:(i + 1)])
        test_periods = dict(periods[(i + 1):])

        # train period
        train_period_res, _ = get_best_assets(alldata, train_periods)
        train_scores = scoring_fun(train_period_res)
        # filter median score
        selected_stocks = train_scores[train_scores > 0].head(n_select).index.tolist()
        train_select_avg_score = train_scores[train_scores > 0].head(n_select).values.mean()
        train_avg_score = train_scores.mean()

        if test_periods:
            # test period
            test_period_res, _ = get_best_assets(alldata, test_periods)
            test_scores = scoring_fun(test_period_res)

            # evaluate
            test_select_avg_score = test_scores[selected_stocks].mean()
            test_avg_score = test_scores.mean()
            n_pos_score = (test_scores[selected_stocks] > 0).sum()
            rate_pos_score = n_pos_score / n_select

            stocks_wins = set(test_scores.head(n_select).index.tolist()).intersection(set(selected_stocks))
            stocks_wins_broader = set(test_scores.head(test_range).index.tolist()).intersection(set(selected_stocks))
            n_stocks_wins = len(stocks_wins)
            n_stocks_wins_broader = len(stocks_wins_broader)

            # evaluate, treat period + asset as data point
            perf_dfs = []
            for stock in selected_stocks:
                perf_df = get_asset_performance(test_period_res, stock)
                perf_df.columns = ["periods", "period_return", "max_drawdown", "return_vs_SPY", "drawdown_vs_SPY"]
                perf_dfs.append(perf_df)
            all_perf_df = pd.concat(perf_dfs, axis=0)

            avg_period_return = all_perf_df["period_return"].mean()
            median_period_return = all_perf_df["period_return"].median()
            avg_max_drawdown = all_perf_df["max_drawdown"].mean()
            median_max_drawdown = all_perf_df["max_drawdown"].median()

            return_pos_rate = (all_perf_df["period_return"] > 0).sum() / len(all_perf_df)
            return_win_benchmark_rate = (all_perf_df["return_vs_SPY"] > 0).sum() / len(all_perf_df)
            drawdown_lt_20_rate = (all_perf_df["max_drawdown"] > drawdown_thld).sum() / len(all_perf_df)
            drawdown_win_benchmark_rate = (all_perf_df["drawdown_vs_SPY"] > drawdown_tol).sum() / len(all_perf_df)

        # save to result
        res[f"test_{i}"] = {}
        res[f"test_{i}"]["train"] = train_periods
        res[f"test_{i}"]["test"] = test_periods
        # TRAIN
        res[f"test_{i}"]["all_stocks"] = train_scores.index.tolist()
        res[f"test_{i}"]["all_stocks_scores"] = train_scores
        res[f"test_{i}"]["train_selected_stocks"] = selected_stocks
        res[f"test_{i}"]["train_selected_avg_score"] = train_select_avg_score
        res[f"test_{i}"]["train_avg_score"] = train_avg_score
        res[f"test_{i}"]["train_raw_results"] = train_period_res

        if test_periods:
            # TEST
            res[f"test_{i}"]["test_selected_avg_score"] = test_select_avg_score
            res[f"test_{i}"]["test_avg_score"] = test_avg_score
            res[f"test_{i}"]["test_pos_score_rate"] = rate_pos_score
            res[f"test_{i}"][f"test_n_stock_stay_{n_select}"] = n_stocks_wins
            res[f"test_{i}"][f"test_n_stock_stay_broader_{test_range}"] = n_stocks_wins_broader
            res[f"test_{i}"][f"test_win_stocks"] = stocks_wins
            res[f"test_{i}"][f"test_win_stocks_broader"] = stocks_wins_broader
            res[f"test_{i}"]["test_raw_results"] = test_period_res
            # Samples
            res[f"test_{i}"]["sample_avg_period_return"] = avg_period_return
            res[f"test_{i}"]["sample_median_period_return"] = median_period_return
            res[f"test_{i}"]["sample_avg_max_drawdown"] = avg_max_drawdown
            res[f"test_{i}"]["sample_median_max_drawdown"] = median_max_drawdown
            res[f"test_{i}"]["sample_return_pos_rate"] = return_pos_rate
            res[f"test_{i}"]["sample_return_win_bechmark_rate"] = return_win_benchmark_rate
            res[f"test_{i}"]["sample_drawdown_lt_20_rate"] = drawdown_lt_20_rate
            res[f"test_{i}"]["sample_drawdown_win_benchmark_rate"] = drawdown_win_benchmark_rate

    return pd.DataFrame(res)
