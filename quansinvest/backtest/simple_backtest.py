import pandas as pd
from yahoo_fin import stock_info as si


def get_data(symbols, dates, colname="adjclose"):
    """Read stock data (adjusted close) for given symbols from CSV files."""
    df = pd.DataFrame(index=dates)

    for symbol in symbols:
        df_temp = si.get_data(symbol)[[colname]]
        df_temp = df_temp.rename(columns={colname: symbol})
        df = df.join(df_temp)

    df.index = pd.to_datetime(df.index)
    df = df.dropna(how="all").fillna(method="ffill").fillna(method="bfill")
    return df


def compute_portvals(
    orders,
    start_val=1000000,
    commission=9.95,
    impact=0.005,
):
    """
    Computes the portfolio values.

    :param orders: orders dataframe
    :param start_val: The starting value of the portfolio
    :type start_val: int
    :param commission: The fixed amount in dollars charged for each transaction (both entry and exit)
    :type commission: float
    :param impact: The amount the price moves against the trader compared to the historical data at each transaction
    :type impact: float
    :return: the result (portvals) as a single-column dataframe, containing the value of the portfolio for each trading day in the first column from start_date to end_date, inclusive.
    :rtype: pandas.DataFrame
    """
    orders.sort_index(inplace=True, ascending=True)

    symbols = orders["Symbol"].unique()
    dates = pd.date_range(orders.index[0], orders.index[-1])

    # load all stocks' price
    assets = get_data(symbols, dates)

    # tracking cash
    account = assets.copy()
    account[:] = 0
    account["Cash"] = 0

    for date, trade in orders.iterrows():
        symbol, order = trade["Symbol"], trade["Order"]
        nshares = trade["Shares"] if order == "BUY" else -trade["Shares"]
        desired_price = assets.loc[date, symbol]
        actual_price = desired_price*(1 + impact) if order == "BUY" else desired_price*(1 - impact)
        amount = nshares * actual_price

        # record
        account.loc[date, symbol] += nshares
        account.loc[date, 'Cash'] = account.loc[date, 'Cash'] - amount - commission

    account["Cash"].iloc[0] += start_val
    account = account.cumsum()

    # calculate portfolio value
    portfolio_values = (account[symbols]*assets[symbols]).sum(axis=1) + account["Cash"]
    return pd.DataFrame(portfolio_values, columns=["Portfolio"])


def evaluate_portfolio(portvals):
    """
    evaluate_portfolio

    Inputs:
    portvals: dataframe, outputs from compute_portvals function
    """
    # Process orders
    if isinstance(portvals, pd.DataFrame):
        portvals = portvals[portvals.columns[0]]  # just get the first column
    else:
        "warning, code did not return a DataFrame"

    # Get portfolio stats
    start_date = portvals.index[0]
    end_date = portvals.index[-1]

    # daily return
    daily_rets = portvals / portvals.shift(1) - 1
    avg_daily_ret = daily_rets.mean()
    std_daily_ret = daily_rets.std()

    # cum return
    cum_ret = portvals.iloc[-1] / portvals.iloc[0] - 1

    # Sharpe
    sharpe = avg_daily_ret / std_daily_ret
    annual_sharpe = sharpe * 252 ** 0.5

    return {
        "Start Date": start_date,
        "End Date": end_date,
        "Cumulative Return": cum_ret,
        "Standard Deviation Daily Return": std_daily_ret,
        "Average Daily Return": avg_daily_ret,
        "Annualized Sharpe Ratio": annual_sharpe,
        "Final Portfolio Value": portvals[-1],
    }
