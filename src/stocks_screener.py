import pandas

from stock_info import *
from global_configuration import INTRADAY_STOCK_MARKET_INFO_TABLE_PATH

import pandas as pd
import numpy as np

from_date = '2024-10-17'
to_date = ''
ticker="ASTR"

class Statistics:
    def __init__(self, ticker: str, df: pandas.DataFrame):
        self.__ticker = ticker
        self.__df = df
        self.__mean_price = None
        self.__mean_volume = None
        self.__mean_price_changing = None
        self.__mean_volume_changing = None

    def get_mean_price_changing(self):
        if self.__mean_price_changing:
            pass
        else:
            self.__mean_price_changing = self.__df['price_change'].mean()
        return self.__mean_price_changing

    def get_mean_volume_changing(self):
        if self.__mean_volume_changing:
            pass
        else:
            self.__mean_volume_changing = self.__df['volume_change'].mean()
        return self.__mean_volume_changing

    def get_mean_price(self):
        if self.__mean_price:
            pass
        else:
            self.__mean_price = self.__df['last_price'].mean()
        return self.__mean_price

    def get_mean_volume(self):
        if self.__mean_volume:
            pass
        else:
            self.__mean_volume = self.__df['last_volume'].mean()
        return self.__mean_volume

    def get_df(self):
        return self.__df

    @staticmethod
    def make_statistics_for_hours(ticker: str, df: pandas.DataFrame) -> list:
        hours_statistics = list()
        for hourly_dfs in [group for _, group in df.groupby(df['datetime'].dt.hour)]:
            hours_statistics.append(Statistics(ticker, hourly_dfs))
        return hours_statistics

    @staticmethod
    def make_statistics_for_days(ticker: str, df: pandas.DataFrame) -> list:
        days_statistics = list()
        for daily_dfs in [group for _, group in df.groupby(df['datetime'].dt.date)]:
            days_statistics.append(Statistics(ticker, daily_dfs))
        return  days_statistics

def sql_rows_to_pandas_data_frames(sql_rows: list) -> pandas.DataFrame:
    df = pd.DataFrame(sql_rows, columns=['last_price', 'last_volume', 'date', 'time'])

    # добавить строку с изменением цены
    df['price_change'] = df['last_price'].diff()
    df.loc[df.index[0], 'price_change'] = 0

    # добавить строку с изменением объемов
    df['volume_change'] = df['last_volume'].diff()
    df.loc[df.index[0], 'volume_change'] = 0

    df['datetime'] = df.apply(lambda row: pd.to_datetime(f"{row['date']} {row['time']}"), axis=1)
    return df

def main():
    conn = sqlite3.connect(INTRADAY_STOCK_MARKET_INFO_TABLE_PATH)
    cursor = conn.cursor()

    rows = StockInfo.get_last_records_from(cursor, ticker, from_date)
    df = sql_rows_to_pandas_data_frames(rows)

    hours_statistics = Statistics.make_statistics_for_hours(ticker, df)
    days_statistics = Statistics.make_statistics_for_days(ticker, df)

    for st in hours_statistics:
        print(f"{st.get_mean_price()}, {st.get_mean_price_changing()}, {st.get_mean_volume()}, {st.get_mean_volume_changing()}")


if __name__=="__main__":
    main()