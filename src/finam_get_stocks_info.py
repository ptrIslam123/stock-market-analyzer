import time
import re

from zipfile import error
from playwright.sync_api import Playwright, sync_playwright, expect
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime

FINAM_BROWSER_CONTEXT_PATH = "/home/islam/PycharmProjects/stock-market-analyzer/.local/finam_context"
FINAM_DATA_SET_SOURCES_URL = "https://www.finam.ru/quotes/stocks/russia/"
STOCK_MARKET_INFO_TABLE_PATH = "/home/islam/PycharmProjects/stock-market-analyzer/database/stock_marker_info_table"

class StockInfo:
    def __init__(self, stock_name, last_deal, price_change_percent, open_price, max_price, min_price, close_price, volume, update_time):
        self.stock_name = stock_name                            # Инструмент
        self.last_deal = last_deal                              # Изменение цен в %
        self.price_change_percent = price_change_percent        # Открытие
        self.open_price = open_price                            # Цена открытия
        self.max_price = max_price                              # Максимальная цена
        self.min_price = min_price                              # Минимальная цена
        self.close_price = close_price                          # Цена закрытия
        self.volume = volume                                    # Объемы, штуки
        self.update_time = update_time                          # Время обновления

    def __repr__(self):
        return (f"StockInfo(stock_name={self.stock_name}, "
                f"last_deal={self.last_deal}, "
                f"price_change_percent={self.price_change_percent}, "
                f"open_price={self.open_price}, "
                f"max_price={self.max_price}, "
                f"min_price={self.min_price}, "
                f"close_price={self.close_price}, "
                f"volume={self.volume}, "
                f"update_time={self.update_time})")


    def to_dict(self):
        return {
            'stock_name': self.stock_name,
            'last_deal': self.__parse_price(self.last_deal),
            'price_change_percent': self.__parse_percent(self.price_change_percent),
            'open_price': self.__parse_price(self.open_price),
            'max_price': self.__parse_price(self.max_price),
            'min_price': self.__parse_price(self.min_price),
            'close_price': self.__parse_price(self.close_price),
            'volume': self.__parse_volume(self.volume),
            'update_time': self.update_time
        }

    def __parse_price(self, price_str: str) -> float:
        # Удаляем символ валюты и заменяем запятую на точку
        if len(price_str) == 0:
            return 0
        else:
            return float(re.sub(r'[^\d,]', '', price_str).replace(',', '.'))

    def __parse_percent(self, percent_str) -> float:
        # Удаляем символ процента и заменяем запятую на точку
        if len(percent_str) == 0:
            return 0

        is_negative = percent_str.startswith('-')
        cleaned_str = re.sub(r'[^\d,]', '', percent_str)
        percent_value = float(cleaned_str.replace(',', '.'))
        if is_negative:
            percent_value = -percent_value

        return percent_value

    def __parse_volume(self, volume_str)-> int:
        # Удаляем пробелы и преобразуем в целое число
        if len(volume_str) == 0:
            return 0
        else:
            return int(re.sub(r'\s', '', volume_str))

def parse_info(page_content: str):
    soup = BeautifulSoup(page_content, 'html.parser')

    table = soup.find('table', id='finfin-local-plugin-quote-table-table-table')

    data = []
    for row in table.find_all('tr'):
        row_data = []
        for cell in row.find_all(['td', 'th']):
            row_data.append(cell.get_text(strip=True))

        if len(row_data) == 9:
            if all(item == "" for item in row_data[1:]):
                pass
            else:
                table_row = StockInfo(*row_data)
                data.append(table_row)

    data.pop(0)
    return data

def normalize_stock_name(stock_name):
    normalized_string = str()
    i = 0
    while i < len(stock_name):
        symbol = stock_name[i]
        if symbol == '\"' or symbol == '\'':
            i += 1
            continue
        elif symbol == '-' or symbol == '+' or symbol == '.':
            normalized_string += '_'
        elif symbol == ' ':
            i += 1
            continue
        elif symbol == '(':
            i += 1
            while i < len(stock_name) and stock_name[i] != ')':
                i += 1
        else:
            normalized_string += symbol
        i += 1
    return normalized_string

def save_to_db(stock_info_data_list, table_path: str):
    conn = sqlite3.connect(table_path + ".db")
    cursor = conn.cursor()

    stocks_name_table = "STOCK_NAMES"

    update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for stock_info_data in stock_info_data_list:
        data = stock_info_data.to_dict()
        stock_name = normalize_stock_name(data["stock_name"])

        create_stock_name_table_sql_re = f"""
            CREATE TABLE IF NOT EXISTS {stocks_name_table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_name TEXT NOT NULL,
                real_stock_name TEXT NOT NULL
            );
        """.format(stocks_name_table=stocks_name_table)

        create_stocks_data_info_table_sql_req = """
            CREATE TABLE IF NOT EXISTS {stock_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_name TEXT NOT NULL,
                last_deal REAL,
                price_change_percent REAL,
                open_price REAL,
                max_price REAL,
                min_price REAL,
                close_price REAL,
                volume INTEGER,
                update_time TEXT
            );
        """.format(stock_name=stock_name)

        try:
            cursor.execute(create_stocks_data_info_table_sql_req)
        except Exception as e:
            print(f"CREATE/OPEN SQL TABLE ERROR(table_name={stock_name}): {error}".format(stock_name=data["stock_name"], error=str(e)))
            return

        try:
            cursor.execute(create_stock_name_table_sql_re)
        except Exception as e:
            print(f"CREATE/OPEN SQL TABLE ERROR(table_name={stocks_name_table}): {error}".format(stocks_name_table=stocks_name_table, error=str(e)))
            return

        insert_stocks_data_sql = f"""
            INSERT INTO {stock_name} (stock_name, last_deal, price_change_percent, open_price, max_price, min_price, close_price, volume, update_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """.format(stock_name=stock_name)

        insert_stocks_name_sql = f"""
            INSERT INTO {stocks_name_table} (stock_name, real_stock_name)
            VALUES (?, ?);
        """.format(stocks_name_table=stocks_name_table)

        try:
            cursor.execute(insert_stocks_data_sql, (
                data["stock_name"],
                data["last_deal"],
                data["price_change_percent"],
                data["open_price"],
                data["max_price"],
                data["min_price"],
                data["close_price"],
                data["volume"],
                update_time
            ))
            conn.commit()
        except Exception as e:
            print(f"INSERT INTO SQL TABLE ERROR(table_name={stock_name}): {error}".format(stock_name=stock_name, error=str(e)))
            return

        try:
            cursor.execute(insert_stocks_name_sql, (stock_name, data["stock_name"]))
            conn.commit()
        except Exception as e:
            print(f"INSERT INTO SQL TABLE ERROR(table_name={stocks_name_table}): {error}".format(stocks_name_table=stocks_name_table, error=str(e)))
            return

    conn.close()

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(storage_state=FINAM_BROWSER_CONTEXT_PATH)
    page = context.new_page()
    page.goto(FINAM_DATA_SET_SOURCES_URL)

    page.get_by_role("button", name="Показать ещё").click()
    page.get_by_role("button", name="Показать ещё").click()
    page.get_by_role("button", name="Показать ещё").click()
    page.get_by_role("button", name="Показать ещё").click()
    page.get_by_role("button", name="Показать ещё").click()
    page.get_by_role("button", name="Показать ещё").click()

    while True:
        time.sleep(3)
        data = parse_info(page.content())
        if len(data) == 0:
            continue
        else:
            save_to_db(data, STOCK_MARKET_INFO_TABLE_PATH)
            break


    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
