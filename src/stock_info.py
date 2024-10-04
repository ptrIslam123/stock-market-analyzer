import sqlite3

class StockInfo:
    def __init__(self, name: str, ticker: str,
                 last_price: float, price_change_percent: float,
                 open_price: float, close_price: float, volume: int,
                 update_time: str):
        self.name = name                                        # Инструмент
        self.ticker = ticker                                    # Тикер инструмента
        self.last_price = last_price                            # Последняя цена
        self.price_change_percent = price_change_percent        # Изменение цен в %
        self.open_price = open_price                            # Цена открытия
        self.close_price = close_price                          # Цена закрытия
        self.volume = volume                                    # Объемы, штуки
        self.update_time = update_time                          # Время обновления
        self.table_name = self.get_table_name(ticker)

    def __repr__(self) -> str:
        return (f"StockInfo(stock_name={self.name}, "
                f"stock_ticker={self.ticker}, "
                f"last_deal={self.last_price}, "
                f"price_change_percent={self.price_change_percent}, "
                f"open_price={self.open_price}, "
                f"close_price={self.close_price}, "
                f"volume={self.volume}, "
                f"update_time={self.update_time})")

    def create_table(self, cursor) -> bool:
        try:
            cursor.execute(self.__create_table_sql_re())
            return True
        except Exception as e:
            print(f"CREATE TABLE={self.ticker} SQL REQ ERROR: {str(e)}")
            return False

    def insert(self, cursor, conn) -> bool:
        try:
            cursor.execute(self.__insert_into_table_sql_req(),
                (
                    self.name,
                    self.last_price,
                    self.price_change_percent,
                    self.open_price,
                    self.close_price,
                    self.volume,
                    self.update_time
                )
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"INSERT INTO TABLE={self.ticker} SQL REQ ERROR: {str(e)}")
            return False

    def __create_table_sql_re(self) -> str:
        return """CREATE TABLE IF NOT EXISTS {table} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        stock_name TEXT NOT NULL,
                        last_price REAL,
                        price_change_percent REAL,
                        open_price REAL,
                        close_price REAL,
                        volume INTEGER,
                        update_time TEXT
                    );
        """.format(table=self.table_name)

    def __insert_into_table_sql_req(self) -> str:
        return """INSERT INTO {table} (stock_name, last_price, price_change_percent, open_price, close_price, volume, update_time)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """.format(table=self.table_name)

    def get_table_name(self, ticker: str) -> str:
        return ticker.replace('-', '_')


