import logging
import re

from global_configuration import TABLE_FOR_5_MIN_PREFIX
from statistics import AggregatedStatistic, Statistics
from stock_info import StockInfo

class DBManager:
    STOCKS_INFO_TABLE_PREFIX="stocks_info_"
    STATISTICS_TABLE_PREFIX="statistics_"

    def __init__(self, cursor, conn):
        self.__cursor = cursor
        self.__conn = conn

    def create_stocks_info_table(self, ticker: str, interval_as_str: str):
        try:
            self.__cursor.execute(self.__create_stocks_info_table_sql_re(ticker, interval_as_str))
        except Exception as e:
            logging.error(f"CREATE TABLE SQL REQ ERROR: {str(e)}")
            raise e

    def create_statistics_table(self, ticker: str, interval_as_str: str):
        try:
            self.__cursor.execute(self.__create_statistics_table_sql_re(ticker, interval_as_str))
        except Exception as e:
            logging.error(f"CREATE TABLE SQL REQ ERROR: {str(e)}")
            raise e

    def insert_stocks_info(self, ticker: str, interval_as_str: str, stocks_info: StockInfo):
        try:
            self.__cursor.execute(self.__insert_into_stocks_info_table_sql_req(ticker, interval_as_str),
                (
                    stocks_info.last_price,
                    stocks_info.last_volume,
                    stocks_info.date,
                    stocks_info.time,
                )
            )
            self.__conn.commit()
        except Exception as e:
            logging.error(f"INSERT INTO TABLE SQL REQ ERROR: {str(e)}")
            raise e

    def insert_statistics_info(
            self, ticker: str, interval_as_str: str,
            stat: Statistics, aggregated_stat: AggregatedStatistic,
            date: str, time: str
    ):
        try:
            self.__cursor.execute(self.__insert_into_statistics_table_sql_req(ticker, interval_as_str),
                (
                    stat.absolute_mean_price_in_percent,
                    stat.price_mad_in_percent,
                    aggregated_stat.absolute_mean_price_for_timeframe_in_percent
                )
            )
            self.__conn.commit()
        except Exception as e:
            logging.error(f"INSERT INTO TABLE SQL REQ ERROR: {str(e)}")
            raise e

    def delete_all_table(self):
        for table in self.get_all_tables():
            self.delete_table(table)

    def delete_stocks_info_table(self, ticker: str, interval_as_str: str):
        try:
            self.__cursor.execute(DBManager.__delete_stocks_info_table_sql_req(ticker, interval_as_str))
            self.__conn.commit()
        except Exception as e:
            logging.error(f"DROP TABLE SQL REQ ERROR: {str(e)}")
            raise e

    def delete_statistics_table(self, table_name: str, interval_as_str: str):
        try:
            self.__cursor.execute(DBManager.__delete_statistics_table_sql_req(table_name, interval_as_str))
            self.__conn.commit()
        except Exception as e:
            logging.error(f"DROP TABLE SQL REQ ERROR: {str(e)}")
            raise e

    def delete_table(self, table_name: str):
        try:
            self.__cursor.execute(f"""DROP TABLE IF EXISTS {table_name} CASCADE;""")
            self.__conn.commit()
        except Exception as e:
            logging.error(f"DROP TABLE SQL REQ ERROR: {str(e)}")
            raise e

    def get_all_tables(self):
        try:
            self.__cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            tables = self.__cursor.fetchall()
            return [table[0] for table in tables]
        except Exception as e:
            logging.error(f"SELECT ALL TABLES: SQL REQ ERROR: {str(e)}")
            raise e

    def get_all_ticker_names(self) -> list[str]:
        ticker_name_list = list()
        pattern = r"_for_\d+.*"
        stocks_info_table_prefix_len = len(DBManager.STOCKS_INFO_TABLE_PREFIX)
        statistics_table_prefix_len = len(DBManager.STATISTICS_TABLE_PREFIX)
        for table in self.get_all_tables():
            if DBManager.STOCKS_INFO_TABLE_PREFIX == table[ : stocks_info_table_prefix_len]:
                ticker = re.sub(pattern, "", table[stocks_info_table_prefix_len : ])
                ticker_name_list.append(ticker)
            if DBManager.STATISTICS_TABLE_PREFIX == table[ : statistics_table_prefix_len]:
                ticker = re.sub(pattern, "", table[statistics_table_prefix_len : ])
                ticker_name_list.append(ticker)

        return ticker_name_list

    def get_records_for_day(self, table_name: str, interval_as_str: str, date_as_str: str) -> list:
        try:
            self.__cursor.execute(self.__get_stocks_info_records_for_day(table_name, interval_as_str), (date_as_str, ))
            return self.__cursor.fetchall()
        except Exception as e:
            logging.error(f"SELECT ALL TABLES: SQL REQ ERROR: {str(e)}")
            raise e

    def get_all_records(self, table_name: str, interval_as_str: str) -> list:
        try:
            self.__cursor.execute(self.__get_all_stocks_info_records(table_name, interval_as_str), ())
            return self.__cursor.fetchall()
        except Exception as e:
            logging.error(f"SELECT ALL TABLES: SQL REQ ERROR: {str(e)}")
            raise e

    @staticmethod
    def __create_stocks_info_table_sql_re(ticker: str, interval_as_str: str) -> str:
        table_name = f"{DBManager.STOCKS_INFO_TABLE_PREFIX}{ticker}_{interval_as_str}"
        return f"""CREATE TABLE IF NOT EXISTS {table_name} (
                            last_price REAL,
                            last_volume BIGINT,
                            date DATE,
                            time TIME
                        );
            """

    @staticmethod
    def __create_statistics_table_sql_re(ticker: str, interval_as_str: str) -> str:
        table_name = f"{DBManager.STATISTICS_TABLE_PREFIX}{ticker}_{interval_as_str}"
        return f"""CREATE TABLE IF NOT EXISTS {table_name} (
                            absolute_mean_price_in_percent REAL,
                            absolute_mean_price_for_whole_market_in_percent REAL,
                            
                            absolute_mean_volume_in_percent REAL,
                            absolute_mean_volume_whole_market_in_percent REAL,
                            
                            date DATE,
                            time TIME
                        );
                """

    @staticmethod
    def __insert_into_stocks_info_table_sql_req(ticker: str, interval_as_str) -> str:
        table_name = f"{DBManager.STOCKS_INFO_TABLE_PREFIX}{ticker}_{interval_as_str}"
        return f"""INSERT INTO {table_name} (last_price, last_volume, date, time)
                    VALUES (%s, %s, %s, %s);
                """

    @staticmethod
    def __insert_into_statistics_table_sql_req(ticker: str, interval_as_str) -> str:
        table_name = f"{DBManager.STATISTICS_TABLE_PREFIX}{ticker}_{interval_as_str}"
        return f"""INSERT INTO {table_name} (...)
                        VALUES (...);
                    """

    @staticmethod
    def __delete_stocks_info_table_sql_req(ticker: str, interval_as_str: str) -> str:
        table_name = f"{DBManager.STOCKS_INFO_TABLE_PREFIX}{ticker}_{interval_as_str}"
        return f"""DROP TABLE IF EXISTS {table_name} CASCADE;"""

    @staticmethod
    def __delete_statistics_table_sql_req(ticker: str, interval_as_str: str) -> str:
        table_name = f"{DBManager.STATISTICS_TABLE_PREFIX}{ticker}_{interval_as_str}"
        return f"""DROP TABLE IF EXISTS {table_name} CASCADE;"""


    @staticmethod
    def __get_stocks_info_records_for_day(ticker: str, interval_as_str: str) -> str:
        table_name = f"{DBManager.STOCKS_INFO_TABLE_PREFIX}{ticker}_{interval_as_str}"
        return f"""SELECT * FROM {table_name} WHERE date = %s;"""

    @staticmethod
    def __get_statistics_records_for_day(ticker: str, interval_as_str: str) -> str:
        table_name = f"{DBManager.STATISTICS_TABLE_PREFIX}{ticker}_{interval_as_str}"
        return f"""SELECT * FROM {table_name} WHERE date = %s;"""


    @staticmethod
    def __get_all_stocks_info_records(ticker: str, interval_as_str: str) -> str:
        table_name = f"{DBManager.STATISTICS_TABLE_PREFIX}{ticker}_{interval_as_str}"
        return f"""SELECT * FROM {table_name};"""

    @staticmethod
    def __get_all_statistics_records(ticker: str, interval_as_str: str) -> str:
        table_name = f"{DBManager.STATISTICS_TABLE_PREFIX}{ticker}_{interval_as_str}"
        return f"""SELECT * FROM {table_name};"""
