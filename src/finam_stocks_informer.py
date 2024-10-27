import time
import datetime
import psycopg2
import asyncio

from datetime import datetime, timedelta
from playwright.sync_api import Playwright, sync_playwright
from global_configuration import (
    FINAM_BROWSER_CONTEXT_PATH,
    FINAM_RUSSIAN_SHARE_DATA_SET_SOURCES_URL,
    STOCKS_MARKET_STORAGE_SIZE_IN_DAYS,
    get_postgresql_config
)
from final_stocks_info_parser import *

def get_shifted_date(days: int):
    date_threshold = datetime.datetime.now() - timedelta(days=days)
    return date_threshold.strftime('%Y-%m-%d')


def run(playwright: Playwright) -> None:
    try:
        config = get_postgresql_config()
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
    except psycopg2.Error as e:
        logging.error(f"POSTGRESQL CONNECTION ERROR: {str(e)}")
        exit()

    for ticker in StockInfo.get_all_tickers(cursor):
        StockInfo.normalize(cursor, conn, ticker, get_shifted_date(STOCKS_MARKET_STORAGE_SIZE_IN_DAYS))

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(storage_state=FINAM_BROWSER_CONTEXT_PATH)
    page = context.new_page()
    page.goto(FINAM_RUSSIAN_SHARE_DATA_SET_SOURCES_URL)

    while True:
        try:
            page.get_by_role("button", name="Показать ещё").click(timeout=7000)
        except:
            break

    while True:
        parser = FinalStocksInfoParser()
        stocks_info_list = parser.parse_stocks(page.content())
        if stocks_info_list:
            for stock_info in stocks_info_list:
                if stock_info.create_table(cursor):
                    if stock_info.insert(cursor, conn):
                        continue
                break
            time.sleep(10)
        else:
            continue
    # ---------------------
    context.close()
    browser.close()

def main():
    with sync_playwright() as playwright:
        run(playwright)

if __name__ == "__main__":
    main()