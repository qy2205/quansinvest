from quansinvest.data.financial import scrapy_income
import yahoo_fin.stock_info as si
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta


def pe_valuation(symbol, est_eps_chg_window=3, forward_look_window=3, return_forward_pe=True):
    """
    :param symbol:
    :param est_eps_chg_window: default = 3 years
    :param forward_look_window: default = 3 years, for estimating forward PE
    :param return_forward_pe: if return current forward PE df
    :return:
    """
    df = scrapy_income(symbol)
    eps_df = df[df["Quarter Ended"] == "EPS (Diluted)"].T.iloc[1:-1]
    eps_df.columns = [symbol]
    eps_df.index = pd.to_datetime(eps_df.index)
    eps_df = eps_df.sort_index()
    eps_df = pd.merge_asof(eps_df, si.get_data(symbol)[["adjclose"]], left_index=True, right_index=True)
    eps_df["EPS_TTM"] = eps_df[symbol].rolling(4).sum()
    eps_df["PE_TTM"] = eps_df["adjclose"] / eps_df["EPS_TTM"]
    eps_df["EPS_TTM_%CHG"] = (eps_df.EPS_TTM - eps_df["EPS_TTM"].shift(1)) / eps_df["EPS_TTM"].shift(1)
    eps_increase = eps_df.tail(4 * est_eps_chg_window)["EPS_TTM_%CHG"].median()
    print(f"EPS Median % Quarterly Increase in recent {est_eps_chg_window} years: ", eps_increase)

    current_price = si.get_data(
        symbol,
        start_date=dt.datetime.now().date() - dt.timedelta(5)
    ).iloc[-1]["adjclose"]

    eps_ttm = eps_df.iloc[-1]["EPS_TTM"]

    # historical forward PE
    eps_df["EPS_%CHG_FORWARD_EST"] = eps_df["EPS_TTM_%CHG"].rolling(est_eps_chg_window*4).mean()
    eps_df["FORWARD_EPS_1y"] = eps_df["EPS_TTM"] * (1 + eps_df["EPS_%CHG_FORWARD_EST"]) ** 4
    eps_df["FORWARD_EPS_2y"] = eps_df["EPS_TTM"] * (1 + eps_df["EPS_%CHG_FORWARD_EST"]) ** 8
    eps_df["FORWARD_EPS_3y"] = eps_df["EPS_TTM"] * (1 + eps_df["EPS_%CHG_FORWARD_EST"]) ** 12

    # current forward PE
    forward_pe_df = None
    if return_forward_pe:
        forward_pes = []
        forward_time = []
        current_time = eps_df.iloc[-1].name
        for i in range(0, 4 * forward_look_window + 1):
            pe = current_price / (eps_ttm * (1 + eps_increase) ** i)
            forward_pes.append(pe)
            forward_time.append(current_time)
            print(f"{current_time} Forward PE = {pe}")
            current_time += relativedelta(months=+3)
        forward_pe_df = pd.DataFrame({"date": forward_time, f"{symbol}_Forward_PE": forward_pes})

    return eps_df, forward_pe_df
