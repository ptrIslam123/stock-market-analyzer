from datetime import datetime, timedelta
from typing import Optional

from tinkoff.invest import Client
from tinkoff.invest.grpc.marketdata_pb2 import *
from tinkoff.invest.schemas import InstrumentIdType, InstrumentStatus
from  stock_info import StockInfo
from global_configuration import *
import sqlite3

with open(TINKOFF_API_TOKEN_PATH, 'r', encoding='utf-8') as file:
    TOKEN = file.read()

def get_russian_companies() -> list:
    with Client(TOKEN) as client:
        # Получаем список всех акций
        shares = client.instruments.shares(instrument_status=InstrumentStatus.INSTRUMENT_STATUS_BASE)

        russian_companies = [
            {
                "ticker": share.ticker,
                "name": share.name,
                "class_code": share.class_code,
                "isin": share.isin,
                "currency": share.currency,
                "lot": share.lot,
                "min_price_increment": share.min_price_increment.units + share.min_price_increment.nano / 1e9
            }
            for share in shares.instruments if share.class_code == RUSSIAN_SHARE_CLASS_CODE
        ]
        return russian_companies


def get_figi_by_ticker(ticker: str) -> Optional[str]:
    with Client(TOKEN) as client:
        try:
            response = client.instruments.share_by(
                id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_TICKER,
                class_code=RUSSIAN_SHARE_CLASS_CODE,
                id=ticker
            )
            return response.instrument.figi
        except Exception as e:
            print(str(e))
            return None

def get_stock_price(figi: str) -> Optional[str]:
    with Client(TOKEN) as client:
        response = client.market_data.get_last_prices(
            figi=[figi]
        )
        if response.last_prices:
            price = response.last_prices[0].price
            return price.units + price.nano / 1e9
        else:
            return None

def get_stock_info(ticker: str) -> Optional[StockInfo]:
    figi = get_figi_by_ticker(ticker)
    with Client(TOKEN) as client:
        # Получаем текущую цену
        current_price = get_stock_price(figi)
        if current_price is None:
            print(f"No current price data available for {ticker}")
            return None

        # Получаем исторические данные за последний день
        from_date = datetime.now() - timedelta(days=1)
        to_date = datetime.now()
        candles = client.market_data.get_candles(
            figi=figi,
            from_=from_date,
            to=to_date,
            interval=CandleInterval.CANDLE_INTERVAL_1_MIN
        )

        if not candles.candles:
            print(f"No historical data available for {ticker}")
            return None

        # Получаем информацию об инструменте
        instrument = client.instruments.share_by(id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI, id=figi).instrument

        # Определяем цену открытия и объем с начала торгов
        first_candle = candles.candles[0]
        open_price = first_candle.open.units + first_candle.open.nano / 1e9
        total_volume = sum(candle.volume for candle in candles.candles)

        # Определяем цену закрытия или текущую цену
        last_candle = candles.candles[-1]
        close_price = last_candle.close.units + last_candle.close.nano / 1e9
        last_deal = current_price

        # Рассчитываем процентное изменение цены
        price_change_percent = ((last_deal - open_price) / open_price) * 100

        # Заполняем структуру StockInfo
        return StockInfo(
            name=instrument.name,
            ticker=ticker,
            last_price=float(last_deal),
            price_change_percent=float(price_change_percent),
            open_price=float(open_price),
            close_price=float(close_price),
            volume=int(total_volume),
            update_time=datetime.now().isoformat()
        )

def get_order_book(ticker: str, depth: int = 50) -> ():
    figi = get_figi_by_ticker(ticker)
    with Client(TOKEN) as client:
        order_book = client.market_data.get_order_book(
            figi=figi,
            depth=depth
        )
        # Извлекаем ордера на продажу (asks) и на покупку (bids)
        asks = [(ask.price.units + ask.price.nano / 1e9, ask.quantity) for ask in order_book.asks]
        bids = [(bid.price.units + bid.price.nano / 1e9, bid.quantity) for bid in order_book.bids]
        return asks, bids


if __name__ == "__main__":
    conn = sqlite3.connect(INTRADAY_STOCK_MARKET_INFO_TABLE_PATH)
    cursor = conn.cursor()

    for company in get_russian_companies():
        name, ticker = company['name'], company['ticker']
        stock_info_list = list()
        stock_info_list.append(get_stock_info(ticker))
        for stock_info in stock_info_list:
            if stock_info:
                print(stock_info)
                stock_info.create_table(cursor=cursor)
                stock_info.insert(cursor=cursor, conn=conn)