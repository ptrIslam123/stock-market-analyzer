import datetime

class StockInfo:
    def __init__(self, ticker: str, last_price: float, last_volume: int):
        self.last_price: float = last_price                            # Последняя цена
        self.last_volume: float = last_volume                          # Объемы на текущий момент времени, в штуках
        self.date: str = self.get_current_date()
        self.time: str = self.get_current_time()
        self.table_name: str = self.get_table_name(ticker)

    def __repr__(self) -> str:
        return (f"StockInfo(table_name={self.table_name}, "
                f"last_deal={self.last_price}, "
                f"last_volume={self.last_volume}, "
                f"date={self.date}, "
                f"time={self.time})")

    @staticmethod
    def get_current_date() -> str:
        """Возвращает текущую дату в формате YYYY-MM-DD."""
        return datetime.datetime.now().strftime('%Y-%m-%d')

    @staticmethod
    def get_current_time() -> str:
        """Возвращает текущее время в формате HH:MM:SS."""
        return datetime.datetime.now().strftime('%H:%M:%S')

    @staticmethod
    def get_table_name(ticker: str) -> str:
        return ticker.replace('-', '_')