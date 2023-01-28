from quansinvest.data.constants import ROOT_DIR
import pandas as pd
import datetime as dt

etfnames = pd.read_csv(f"{ROOT_DIR}/resources/etfnames.csv")


class ClassPropertyDescriptor(object):

    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()

    def __set__(self, obj, value):
        if not self.fset:
            raise AttributeError("can't set attribute")
        type_ = type(obj)
        return self.fset.__get__(obj, type_)(value)

    def setter(self, func):
        if not isinstance(func, (classmethod, staticmethod)):
            func = classmethod(func)
        self.fset = func
        return self


def classproperty(func):
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)

    return ClassPropertyDescriptor(func)


def etf_name_map(x):
    if len(etfnames[etfnames["Symbol"] == x]) > 0:
        return etfnames[etfnames["Symbol"] == x]["Fund Name"].values[0]
    else:
        return ""


def etf_asset_class_map(x):
    if len(etfnames[etfnames["Symbol"] == x]) > 0:
        return etfnames[etfnames["Symbol"] == x]["Asset Class"].values[0]
    else:
        return ""


# economics cycles move time
def adjust_economics_cycles(
    periods: dict[str: str],
    start_forward: int = None,
    start_backward: int = None,
    end_forward: int = None,
    end_backward: int = None,
):
    new_periods = {}
    for k, v in periods.items():
        k = pd.to_datetime(k).date()
        v = pd.to_datetime(v).date()
        if start_forward is not None:
            k = k + dt.timedelta(start_forward)
        if start_backward is not None:
            k = k - dt.timedelta(start_backward)
        if end_forward is not None:
            v = v + dt.timedelta(end_forward)
        if end_backward is not None:
            v = v - dt.timedelta(end_backward)
        k = str(k)
        v = str(v)
        new_periods[k] = v
    return new_periods


if __name__ == "__main__":
    print(etf_name_map("SPY"))
    print(etf_asset_class_map("SPY"))
