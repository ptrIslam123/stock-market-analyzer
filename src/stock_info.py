import logging
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

    def create_table(self, cursor) -> bool:
        try:
            cursor.execute(self.__create_table_sql_re())
            return True
        except Exception as e:
            logging.error(f"CREATE TABLE={self.table_name} SQL REQ ERROR: {str(e)}")
            return False

    def insert(self, cursor, conn) -> bool:
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
    def delete_table(cursor, conn, table_name: str) -> bool:
        try:
            cursor.execute(StockInfo.__delete_table_sql_req(table_name))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"DROP TABLE={table_name} SQL REQ ERROR: {str(e)}")
            return False

    @staticmethod
    def get_all_records(cursor, table_name: str) -> list:
        try:
            cursor.execute(f"""SELECT * FROM {table_name};""")
            return cursor.fetchall()
        except Exception as e:
            logging.error(f"SELECT TABLE={table_name} SQL REQ ERROR: {str(e)}")
            return list()

    @staticmethod
    def get_last_records_from(cursor, table_name: str, from_date: str) -> list:
        try:
            cursor.execute(StockInfo.__get_last_records(table_name=table_name), (from_date,))
            return cursor.fetchall()
        except Exception as e:
            logging.error(f"SELECT TABLE={table_name} SQL REQ ERROR: {str(e)}")
            return list()

    @staticmethod
    def get_records_from(cursor, table_name: str, from_date: str, to_date: str) -> list:
        try:
            cursor.execute(StockInfo.__get_records(table_name=table_name), (from_date,))
            return cursor.fetchall()
        except Exception as e:
            logging.error(f"SELECT TABLE={table_name} SQL REQ ERROR: {str(e)}")
            return list()

    @staticmethod
    def get_first_n_records(cursor, table_name: str, n: int) -> list:
        try:
            cursor.execute(StockInfo.__get_first_n_records(table_name=table_name), (n,))
            return cursor.fetchall()
        except Exception as e:
            logging.error(f"SELECT TABLE={table_name} SQL REQ ERROR: {str(e)}")
            return list()

    @staticmethod
    def get_all_tickers(cursor) -> list:
        try:
            cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            tables = cursor.fetchall()
            return [table[0] for table in tables]
        except Exception as e:
            logging.error(f"SELECT ALL TABLES: SQL REQ ERROR: {str(e)}")
            return list()

    @staticmethod
    def normalize(cursor, conn, table_name: str, date_threshold: str) -> bool:
        try:
            cursor.execute(f"""DELETE FROM {table_name} WHERE date < %s;""", (date_threshold,))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"DELETE FROM {table_name}: SQL REQ ERROR: {str(e)}")
            return False

    def __create_table_sql_re(self) -> str:
        return f"""CREATE TABLE IF NOT EXISTS {self.table_name} (
                        last_price REAL,
                        last_volume BIGINT,
                        date DATE,
                        time TIME
                    );
        """

    def __insert_into_table_sql_req(self) -> str:
        return f"""INSERT INTO {self.table_name} (last_price, last_volume, date, time)
                VALUES (%s, %s, %s, %s);
            """

    @staticmethod
    def __delete_table_sql_req(table_name: str) -> str:
        return f"""DROP TABLE IF EXISTS {table_name} CASCADE;"""

    @staticmethod
    def __get_last_records(table_name: str) -> str:
        return f"""
            SELECT * 
            FROM {table_name} 
            WHERE date >= %s;
        """

    @staticmethod
    def __get_first_n_records(table_name: str) -> str:
        return f"""SELECT * FROM {table_name} LIMIT %s;"""

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


def delete_all_tables(cursor, conn):
    for ticker in StockInfo.get_all_tickers(cursor):
        StockInfo.delete_table(cursor, conn, ticker)