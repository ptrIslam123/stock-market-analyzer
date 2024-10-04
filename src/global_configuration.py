import os

FINAM_RUSSIAN_SHARE_DATA_SET_SOURCES_URL = "https://www.finam.ru/quotes/stocks/russia/"
FINAM_URL = "https://www.finam.ru/"


ROOT_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/.."
FINAM_BROWSER_CONTEXT_PATH = f"{ROOT_PATH}/.local/finam_context"
INTRADAY_STOCK_MARKET_INFO_TABLE_PATH=f"{ROOT_PATH}/database/intraday_stock_marker_info_table.db"

TINKOFF_API_TOKEN_PATH=f"{ROOT_PATH}/.local/tinkoff_read_only_token"

RUSSIAN_SHARE_CLASS_CODE="TQBR"