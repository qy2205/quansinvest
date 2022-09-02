"""
1. Daily, Weekly, Semi-monthly, Monthly and Yearly return of different assets and strategies
2. performance in presidential election and midterm election years
3. Christmas and other holidays
4. weekday performance
"""
from quansinvest.data.constants import DAILY_RETURN_COLUMN_NAME


def get_freq_return(data, freq: str = "month"):
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
