import pandas as pd
from IPython.display import display
from quansinvest.evaluation.metrics.maxloss import MaxLoss
from quansinvest.evaluation.metrics.maxprofit import MaxProfit


def bigdrop_forward_return_summary_statistics(bigdrop_statistics_results, name="nasdaq", display_dataframe=True):
    next_day_returns = pd.Series(
        [each_period[-1].get("period_return", 0) for each_period in bigdrop_statistics_results])
    drop_prob = (next_day_returns < 0).sum() / len(next_day_returns)
    print(f"{name} 下跌概率: ", drop_prob)
    print(f"{name} 上涨概率: ", 1 - drop_prob)
    print(f"{name} 平均涨跌幅：", next_day_returns.mean())
    print(f"{name} 中位数涨跌幅：", next_day_returns.median())

    print(f"{name} 最大涨幅：", next_day_returns.max())
    print(f"{name} 最大涨幅当日回顾")
    max_return_index = next_day_returns[next_day_returns == next_day_returns.max()].index[0]
    print("max return index: ", max_return_index)
    if display_dataframe:
        display(bigdrop_statistics_results[max_return_index][1])

    print(f"{name} 最大跌幅：", next_day_returns.min())
    print(f"{name} 最大跌幅当日回顾")
    min_return_index = next_day_returns[next_day_returns == next_day_returns.min()].index[0]
    print("min return index: ", min_return_index)
    if display_dataframe:
        display(bigdrop_statistics_results[min_return_index][1])


def bigdrop_forward_return_eval_metrics(
    bigdrop_statistics_results,
    eval_metrics=(MaxLoss(), MaxProfit()),
    name="nasdaq",
    display_dataframe=True,
):
    eval_results = {}
    for eval_metric in eval_metrics:
        eval_results[eval_metric.name] = []
    for period_dfs in bigdrop_statistics_results:
        for eval_metric in eval_metrics:
            # sequential patterns
            if isinstance(period_dfs[0], list):
                period_df = pd.concat([pd.concat(period_dfs[0]), period_dfs[1]], axis=0)
            else:
                period_df = pd.concat([period_dfs[0], period_dfs[1]], axis=0)
            eval_results[eval_metric.name].append(eval_metric(period_df))
    eval_results_df = pd.DataFrame(eval_results)

    if MaxLoss.name in eval_results_df.columns:
        eval_res_with_drawback = eval_results_df[eval_results_df[MaxLoss.name] < 0]
        drawback_prob = len(eval_res_with_drawback)/len(eval_results_df)
        print(f"{name} 未来有损失的概率： ", drawback_prob)
        print(f"{name} 未来无损失的概率： ", 1 - drawback_prob)
        print(f"{name} 损失中位数： ", eval_res_with_drawback[MaxLoss.name].median())
        print(f"{name} 损失平均数： ", eval_res_with_drawback[MaxLoss.name].mean())

        max_loss = eval_res_with_drawback[MaxLoss.name].min()
        print(f"{name} 最大损失： ", max_loss)
        print(f"{name} 最大损失当日回顾")
        max_loss_index = eval_results_df[eval_results_df[MaxLoss.name] == max_loss].index[0]
        print("max loss index: ", max_loss_index)
        if display_dataframe:
            display(bigdrop_statistics_results[max_loss_index][1])

        min_loss = eval_res_with_drawback[MaxLoss.name].max()
        print("最小损失： ", min_loss)
        print(f"{name} 最小损失当日回顾")
        min_loss_index = eval_results_df[eval_results_df[MaxLoss.name] == min_loss].index[0]
        print("min loss index: ", min_loss_index)
        if display_dataframe:
            display(bigdrop_statistics_results[min_loss_index][1])

    if MaxProfit.name in eval_results_df.columns:
        eval_res_pos_profit = eval_results_df[eval_results_df[MaxProfit.name] > 0]
        pos_profit_prob = len(eval_res_pos_profit)/len(eval_results_df)
        print(f"{name} 未来无盈利机会的概率： ", 1 - pos_profit_prob)
        print(f"{name} 未来有盈利机会的概率： ", pos_profit_prob)
        print(f"{name} 盈利中位数： ", eval_res_pos_profit[MaxProfit.name].median())
        print(f"{name} 盈利平均数： ", eval_res_pos_profit[MaxProfit.name].mean())

        max_profit = eval_res_pos_profit[MaxProfit.name].max()
        print(f"{name} 最大收益： ", max_profit)
        print(f"{name} 最大收益当日回顾")
        max_profit_index = eval_results_df[eval_results_df[MaxProfit.name] == max_profit].index[0]
        print("max profit index: ", max_profit_index)
        if display_dataframe:
            display(bigdrop_statistics_results[max_profit_index][1])

        min_profit = eval_res_pos_profit[MaxProfit.name].min()
        print(f"{name} 最小收益： ", min_profit)
        print(f"{name} 最小收益当日回顾")
        min_profit_index = eval_results_df[eval_results_df[MaxProfit.name] == min_profit].index[0]
        print("min profit index: ", min_profit_index)
        if display_dataframe:
            display(bigdrop_statistics_results[min_profit_index][1])

    return eval_results_df
