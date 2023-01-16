from quansinvest.data.constants import ROOT_DIR
import pandas as pd

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


if __name__ == "__main__":
    print(etf_name_map("SPY"))
    print(etf_asset_class_map("SPY"))
