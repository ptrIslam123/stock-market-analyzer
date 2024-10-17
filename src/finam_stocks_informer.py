import time
import sqlite3

from playwright.sync_api import Playwright, sync_playwright
from global_configuration import FINAM_BROWSER_CONTEXT_PATH, INTRADAY_STOCK_MARKET_INFO_TABLE_PATH, FINAM_RUSSIAN_SHARE_DATA_SET_SOURCES_URL
from src.final_stocks_info_parser import *

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(storage_state=FINAM_BROWSER_CONTEXT_PATH)
    page = context.new_page()
    page.goto(FINAM_RUSSIAN_SHARE_DATA_SET_SOURCES_URL)

    while True:
        try:
            page.get_by_role("button", name="Показать ещё").click(timeout=7000)
        except:
            break

    conn = sqlite3.connect(INTRADAY_STOCK_MARKET_INFO_TABLE_PATH)
    cursor = conn.cursor()
    parser = FinalStocksInfoParser()

    while True:
        stocks_info_list = parser.parse_stocks(page.content())
        if stocks_info_list:
            for stock_info in stocks_info_list:
                stock_info.create_table(cursor)
                stock_info.insert(cursor, conn)
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