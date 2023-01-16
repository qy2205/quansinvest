import os

CLOSE_PRICE_COLUMN_NAME = "close"
ADJ_CLOSE_PRICE_COLUMN_NAME = "adjclose"
OPEN_PRICE_COLUMN_NAME = "open"
HIGH_PRICE_COLUMN_NAME = "high"
LOW_PRICE_COLUMN_NAME = "low"
TICKER_COLUMN_NAME = "ticker"
DATE_COLUMN_NAME = "index"
VOLUME_COLUMN_NAME = "volume"
MARKET_DATA_COLUMNS = [
    OPEN_PRICE_COLUMN_NAME,
    HIGH_PRICE_COLUMN_NAME,
    LOW_PRICE_COLUMN_NAME,
    ADJ_CLOSE_PRICE_COLUMN_NAME,
    VOLUME_COLUMN_NAME,
    TICKER_COLUMN_NAME,
]
DAILY_RETURN_COLUMN_NAME = "daily_return"

ASSET_LIST = [
    # gold; silver; gold miners; junior gold miners
    "GLD", "SLV", "GDX", "GDXJ",
    # bond 7-10 years; 20 years+; invest grade corporate bond; 1-3 years; 0-3 month; all bond
    "IEF", "TLT", "LQD", "SHY", "BIL", "AGG",
    # tech; software; semiconductor; technology;
    "QQQ", "IGV", "SOXX", "XLK",
    # aerospace & defense
    "PPA",
    # preferred stocks
    "PFF",
    # energy; energy; oil & gas exploration; oil service;
    "XLE", "IYE", "XOP", "OIH",
    # finance; bank; regional bank
    "XLF", "KBE", "KRE",
    # utilities; retail;
    "XLU", "XRT",
    # industrial; materials; metals and mining; copper;
    "XLI", "XLB", "XME", "CPER",
    # healthcare; medical device; insurance; bio tech;
    "XLV", "IHI", "KIE", "IBB",
    # non-essential products; essential products;
    "XLY", "XLP",
    # real estate; home builder; home construction; real estate
    "IYR", "XHB", "ITB", "VNQ",
    # telecommunication; telecommunication, transportation
    "XTL", "IYZ", "IYT",
    # natural gas; natural gas 12 month; oil; commodity; 
    "UNG", "UNL", "USO", "DBC",
    # benchmark
    "SPY", "DIA",
    # China stock
    "FXI",
]

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
