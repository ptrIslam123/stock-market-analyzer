import time
import re

from playwright.sync_api import Playwright, sync_playwright, expect
from bs4 import BeautifulSoup

FINAM_BROWSER_CONTEXT_PATH = "/home/islam/PycharmProjects/stock-market-analyzer/.local/finam_context"
FINAM_DATA_SET_SOURCES_URL = "https://www.finam.ru/quotes/stocks/russia/"

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
    is_first_row = True
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
            for d in data:
                print(d)

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
