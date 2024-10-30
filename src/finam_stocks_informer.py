import time
import datetime
import psycopg2

from datetime import datetime, timedelta
from playwright.sync_api import Playwright, sync_playwright
from global_configuration import (
    FINAM_BROWSER_CONTEXT_PATH,
    FINAM_RUSSIAN_SHARE_DATA_SET_SOURCES_URL,
    TABLE_FOR_10_SEC_PREFIX,
    TABLE_FOR_5_MIN_PREFIX,
    TABLE_FOR_30_MIN_PREFIX,
    TABLE_FOR_1_HOUR_PREFIX,
    TABLE_FOR_5_HOUR_PREFIX,
    get_postgresql_config
)
from final_stocks_info_parser import *
from db_manager import DBManager

TIMEOUT_FOR_10_SEC=10
TIMEOUT_FOR_1_MIN_IN_SEC=TIMEOUT_FOR_10_SEC * 6
TIMEOUT_FOR_5_MIN_IN_SEC=TIMEOUT_FOR_1_MIN_IN_SEC * 5
TIMEOUT_FOR_30_MIN_IN_SEC=TIMEOUT_FOR_1_MIN_IN_SEC * 30
TIMEOUT_FOR_1_HOUR_IN_SEC=TIMEOUT_FOR_1_MIN_IN_SEC * 60
TIMEOUT_FOR_5_HOUR_IN_SEC=TIMEOUT_FOR_1_HOUR_IN_SEC * 5

def get_shifted_date(days: int):
    date_threshold = datetime.now() - timedelta(days=days)
    return date_threshold.strftime('%Y-%m-%d')

def save_stocks_info(db_manager: DBManager, stocks_info_list: list[StockInfo], cursor, conn, interval_as_str: str):
    if stocks_info_list:
        for stock_info in stocks_info_list:
            table_name = stock_info.table_name
            db_manager.create_stocks_info_table(table_name, interval_as_str)
            db_manager.insert_stocks_info(table_name, interval_as_str, stock_info)

def run(playwright: Playwright) -> None:
    try:
        config = get_postgresql_config()
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
    except psycopg2.Error as e:
        logging.error(f"POSTGRESQL CONNECTION ERROR: {str(e)}")
        return

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(storage_state=FINAM_BROWSER_CONTEXT_PATH)
    page = context.new_page()
    page.goto(FINAM_RUSSIAN_SHARE_DATA_SET_SOURCES_URL)

    while True:
        try:
            page.get_by_role("button", name="Показать ещё").click(timeout=7000)
        except:
            break

    timer_for_5_min = 0
    timer_for_30_min = 0
    timer_for_1_hour = 0
    timer_for_5_hour = 0
    try:
        parser = FinalStocksInfoParser()
        db_manager = DBManager(cursor, conn)
        while True:
            time.sleep(TIMEOUT_FOR_10_SEC)

            stocks_info_list = parser.parse_stocks(page.content())
            save_stocks_info(db_manager, stocks_info_list, cursor, conn, TABLE_FOR_10_SEC_PREFIX)

            timer_for_5_min = (timer_for_5_min + TIMEOUT_FOR_10_SEC) % TIMEOUT_FOR_5_MIN_IN_SEC
            timer_for_30_min = (timer_for_30_min + TIMEOUT_FOR_10_SEC) % TIMEOUT_FOR_30_MIN_IN_SEC
            timer_for_1_hour = (timer_for_1_hour + TIMEOUT_FOR_10_SEC) % TIMEOUT_FOR_1_HOUR_IN_SEC
            timer_for_5_hour = (timer_for_5_hour + TIMEOUT_FOR_10_SEC) % TIMEOUT_FOR_5_HOUR_IN_SEC

            if timer_for_5_min == 0:
                save_stocks_info(db_manager, stocks_info_list, cursor, conn, TABLE_FOR_5_MIN_PREFIX)

            if timer_for_30_min == 0:
                save_stocks_info(db_manager, stocks_info_list, cursor, conn, TABLE_FOR_30_MIN_PREFIX)

            if timer_for_1_hour == 0:
                save_stocks_info(db_manager, stocks_info_list, cursor, conn, TABLE_FOR_1_HOUR_PREFIX)

            if timer_for_5_hour == 0:
                save_stocks_info(db_manager, stocks_info_list, cursor, conn, TABLE_FOR_5_HOUR_PREFIX)

    except Exception as e:
        logging.error(f"Runtime error: {str(e)}")
        context.close()
        browser.close()
        return

def main():
    with sync_playwright() as playwright:
        run(playwright)

if __name__ == "__main__":
    main()