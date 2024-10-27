import os
import json
import logging

FINAM_RUSSIAN_SHARE_DATA_SET_SOURCES_URL="https://www.finam.ru/quotes/stocks/russia/"
FINAM_URL="https://www.finam.ru/"
SMART_LAB_NEWS_URL="https://smartlab.news/"

ROOT_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/.."
FINAM_BROWSER_CONTEXT_PATH = f"{ROOT_PATH}/.local/finam_context"
INTRADAY_STOCK_MARKET_INFO_TABLE_PATH=f"{ROOT_PATH}/database/intraday_stock_marker_info_table.db" # stocks_marker_info

POSTGRESQL_CONFIG_PATH=f"{ROOT_PATH}/.local/postgresql_config.json"

TINKOFF_API_TOKEN_PATH=f"{ROOT_PATH}/.local/tinkoff_read_only_token"

RUSSIAN_SHARE_CLASS_CODE="TQBR"

LOG_FILE_PATH=f"{ROOT_PATH}/log/log.txt"

STOCKS_MARKET_STORAGE_SIZE_IN_DAYS=7

logging.basicConfig(
    filename=LOG_FILE_PATH,
    filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

def get_postgresql_config() -> dict:
    with open(POSTGRESQL_CONFIG_PATH, 'r', encoding='utf-8') as file:
        config_data = json.load(file)
        return config_data