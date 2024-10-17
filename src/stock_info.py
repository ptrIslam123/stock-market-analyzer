import logging
import sqlite3
import datetime

class StockInfo:
    def __init__(self, ticker: str, last_price: float, last_volume: int):
        self.last_price = last_price                            # Последняя цена
        self.last_volume = last_volume                          # Объемы на текущий момент времени, в штуках
        self.date = self.get_current_date()
        self.time = self.get_current_time()
        self.table_name = self.get_table_name(ticker)

    def __repr__(self) -> str:
        return (f"StockInfo(table_name={self.table_name}, "
                f"last_deal={self.last_price}, "
                f"last_volume={self.last_volume}, "
                f"date={self.date}, "
                f"time={self.time})")

    def create_table(self, cursor: sqlite3.Cursor) -> bool:
        try:
            cursor.execute(self.__create_table_sql_re())
            return True
        except Exception as e:
            logging.error(f"CREATE TABLE={self.table_name} SQL REQ ERROR: {str(e)}")
            return False

    def insert(self, cursor: sqlite3.Cursor, conn: sqlite3.Connection) -> bool:
        try:
            cursor.execute(self.__insert_into_table_sql_req(),
                (
                    self.last_price,
                    self.last_volume,
                    self.date,
                    self.time,
                )
            )
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"INSERT INTO TABLE={self.table_name} SQL REQ ERROR: {str(e)}")
            return False

    @staticmethod
    def get_last_records_from(cursor: sqlite3.Cursor, table_name: str, from_date: str) -> list:
        try:
            cursor.execute(StockInfo.__get_last_records(table_name=table_name), (from_date,))
            return cursor.fetchall()
        except Exception as e:
            logging.error(f"SELECT TABLE={table_name} SQL REQ ERROR: {str(e)}")
            return list()

    @staticmethod
    def get_records_from(cursor: sqlite3.Cursor, table_name: str, from_date: str, to_date: str):
        try:
            cursor.execute(StockInfo.__get_records(table_name=table_name), (from_date,))
            return cursor.fetchall()
        except Exception as e:
            logging.error(f"SELECT TABLE={table_name} SQL REQ ERROR: {str(e)}")
            return list()

    def __create_table_sql_re(self) -> str:
        return """CREATE TABLE IF NOT EXISTS {table} (
                        last_price REAL,
                        last_volume INTEGER,
                        date TEXT,
                        time TEXT
                    );
        """.format(table=self.table_name)

    def __insert_into_table_sql_req(self) -> str:
        return """INSERT INTO {table} (last_price, last_volume, date, time)
                VALUES (?, ?, ?, ?);
            """.format(table=self.table_name)

    @staticmethod
    def __get_last_records(table_name: str) -> str:
        return f"""
            SELECT * 
            FROM {table_name} 
            WHERE date >= ?;
        """

    @staticmethod
    def __get_records(table_name: str) -> str:
        return f"""
            SELECT * 
            FROM {table_name} 
            WHERE date BETWEEN ? AND ?;
        """

    @staticmethod
    def get_current_date():
        """Возвращает текущую дату в формате YYYY-MM-DD."""
        return datetime.datetime.now().strftime('%Y-%m-%d')

    @staticmethod
    def get_current_time():
        """Возвращает текущее время в формате HH:MM:SS."""
        return datetime.datetime.now().strftime('%H:%M:%S')

    @staticmethod
    def get_table_name(ticker: str) -> str:
        return ticker.replace('-', '_')


