import psycopg2

from datetime import datetime, timedelta
from db_manager import DBManager
from global_configuration import (
    get_postgresql_config,
    STOCKS_MARKET_STORAGE_SIZE_IN_DAYS,
    TABLE_FOR_5_MIN_PREFIX,
    TABLE_FOR_30_MIN_PREFIX,
    TABLE_FOR_1_HOUR_PREFIX,
    TABLE_FOR_5_HOUR_PREFIX,
    logging
)
from src.finam_news_informer import parse_info
from stock_info import *
from statistics import *

def get_shifted_date(days: int) -> str:
    date_threshold = datetime.datetime.now() - timedelta(days=days)
    return date_threshold.strftime('%Y-%m-%d')

def calculate_ticker_day_stat(db_manager: DBManager, ticker: str, day_as_str: str) -> DayStatistic:
    rows = db_manager.get_records_for_day(ticker, TABLE_FOR_5_MIN_PREFIX, day_as_str)
    stat_for_5_min = Statistics(ticker, rows)

    rows = db_manager.get_records_for_day(ticker, TABLE_FOR_30_MIN_PREFIX, day_as_str)
    stat_for_30_min = Statistics(ticker, rows)

    rows = db_manager.get_records_for_day(ticker, TABLE_FOR_1_HOUR_PREFIX, day_as_str)
    stat_for_1_hour = Statistics(ticker, rows)

    rows = db_manager.get_records_for_day(ticker, TABLE_FOR_5_HOUR_PREFIX, day_as_str)
    stat_for_5_hour = Statistics(ticker, rows)
    return DayStatistic(stat_for_5_min, stat_for_30_min, stat_for_1_hour, stat_for_5_hour)

def calculate_ticker_day_and_aggregated_stat(db_manager: DBManager, day_as_str: str) -> (list[AggregatedStatistic], list[DayStatistic]):
    aggregated_stat_for_5_min = AggregatedStatistic()
    aggregated_stat_for_30_min = AggregatedStatistic()
    aggregated_stat_for_1_hour = AggregatedStatistic()
    aggregated_stat_for_5_hour = AggregatedStatistic()

    aggregated_stat_list: list[AggregatedStatistic] = [
        aggregated_stat_for_5_min, aggregated_stat_for_30_min,
        aggregated_stat_for_1_hour, aggregated_stat_for_5_hour
    ]
    tickers_day_stat_list: list[DayStatistic] = []

    for ticker in db_manager.get_all_ticker_names():
        try:
            ticker_day_stat: DayStatistic = calculate_ticker_day_stat(db_manager, ticker, day_as_str)
            aggregated_stat_for_5_min.use_day_stat(ticker_day_stat.stat_for_5_min)
            aggregated_stat_for_30_min.use_day_stat(ticker_day_stat.stat_for_30_min)
            aggregated_stat_for_1_hour.use_day_stat(ticker_day_stat.stat_for_1_hour)
            aggregated_stat_for_5_hour.use_day_stat(ticker_day_stat.stat_for_5_hour)

            tickers_day_stat_list.append(ticker_day_stat)
        except Exception as e:
            logging.error(f"Invalid ticker={ticker} day statistic structure data: {str(e)}. Skip this instance!")
            continue

    for aggregated_stat in aggregated_stat_list:
        aggregated_stat.complete_calculation()

    return aggregated_stat_list, tickers_day_stat_list

def save_statistics(db_manager: DBManager, aggregated_stat: list[AggregatedStatistic], tickers_day_stat: list[DayStatistic]):
    for ticker_day_stat in tickers_day_stat:
        print(f"for 5 min {ticker_day_stat.stat_for_5_min}\n")
        ticker = ticker_day_stat.stat_for_5_min.ticker
        # db_manager.create_statistics_table(ticker, TABLE_FOR_5_MIN_PREFIX)
        # db_manager.insert_statistics_info(
        #     ticker, TABLE_FOR_5_MIN_PREFIX,
        #     ticker_day_stat.stat_for_5_min, aggregated_stat[0],
        #     "date?", "time?"
        # )

        # ...

def main():
    try:
        config = get_postgresql_config()
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
    except psycopg2.Error as e:
        logging.error(f"POSTGRESQL CONNECTION ERROR: {str(e)}")
        return

    db_manager: DBManager = DBManager(cursor, conn)
    day = get_shifted_date(0)
    aggregated_stat, tickers_day_stat = calculate_ticker_day_and_aggregated_stat(db_manager, day)
    save_statistics(db_manager, aggregated_stat, tickers_day_stat)

    print("\n")

if __name__=="__main__":
    main()