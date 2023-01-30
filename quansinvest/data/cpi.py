import requests
import pandas as pd
from io import StringIO
import datetime as dt


def get_cpi_data(save=False):
    # source: https://fred.stlouisfed.org/series/CPIAUCSL#0
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo" \
          "=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%2344444" \
          "4&ts=12&tts=12&width=1168&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=ye" \
          "s&id=CPIAUCSL&scale=left&cosd=1947-01-01&coed=2022-12-01&line_color=%234572a7&link_values=false" \
          "&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Monthly&fam=avg&" \
          "fgst=lin&fgsnd=2020-02-01&line_index=1&transformation=lin&vintage_date=2023-01-29&revision_date=" \
          "2023-01-29&nd=1947-01-01"
    r = requests.get(url)
    decoded_text = StringIO(r.content.decode('utf-8'))
    cpi_data = pd.read_csv(decoded_text).rename({"DATE": "date", "CPIAUCSL": "CPI"}, axis=1)
    cpi_data["date"] = cpi_data["date"].map(pd.to_datetime)

    # source: https://alfred.stlouisfed.org/release/downloaddates?rid=10
    url = "https://alfred.stlouisfed.org/release/downloaddates?rid=10&ff=txt"
    r = requests.get(url)
    cpi_release_date = pd.DataFrame(
        {"release_date": r.content.decode().split("Release Dates:\r\n\r\n")[1].split("\r\n")})
    cpi_release_date = cpi_release_date[cpi_release_date["release_date"] != ""]
    cpi_release_date["release_date"] = cpi_release_date["release_date"].map(pd.to_datetime)

    # merge and data cleaning
    cpi_data = pd.merge_asof(cpi_release_date, cpi_data, left_on="release_date", right_on="date", direction="backward")
    cpi_data["release_date_ym"] = cpi_data["release_date"].map(lambda x: f"{x.year}_{x.month}")
    cpi_data = cpi_data.groupby("release_date_ym", as_index=False).max()
    del cpi_data["release_date_ym"]
    cpi_data = cpi_data.sort_values(by="date")
    cpi_data["release_date"] = cpi_data["release_date"].shift(-1)
    cpi_data = cpi_data.dropna()
    cpi_data["year"] = cpi_data["date"].map(lambda x: x.year)
    cpi_data["month"] = cpi_data["date"].map(lambda x: x.month)
    cpi_data = cpi_data[cpi_data["year"] >= 1997]

    # validation
    # release date is always in the next month
    assert len(cpi_data[cpi_data.apply(lambda df: df.release_date.month - (df.date + dt.timedelta(40)).month != 0,
                                       axis=1)]) == 0
    # we have 12-month records each year
    assert (cpi_data.groupby("year").month.sum() != (1 + 12) * 12 / 2).sum() == 0

    del cpi_data["date"]

    # calculate YoY and MoM
    cpi_data["CPI_MoM"] = cpi_data["CPI"].pct_change()
    cpi_data["CPI_YoY"] = cpi_data["CPI"].pct_change(12)

    # save data
    if save:
        cpi_data.to_csv("cpi.csv", index=False)

    return cpi_data
