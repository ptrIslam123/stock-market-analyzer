import psycopg2

from datetime import datetime, timedelta
from stock_info import *
from global_configuration import get_postgresql_config, STOCKS_MARKET_STORAGE_SIZE_IN_DAYS
from statistics import *

def get_shifted_date(days: int):
    date_threshold = datetime.datetime.now() - timedelta(days=days)
    return date_threshold.strftime('%Y-%m-%d')

def main():
    try:
        config = get_postgresql_config()
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
    except psycopg2.Error as e:
        logging.error(f"POSTGRESQL CONNECTION ERROR: {str(e)}")
        return

    for ticker in StockInfo.get_all_tickers(cursor):
        StockInfo.normalize(cursor, conn, ticker, get_shifted_date(STOCKS_MARKET_STORAGE_SIZE_IN_DAYS))
        rows = StockInfo.get_all_records(cursor, ticker)
        if not rows:
            continue

        df = sql_rows_to_pandas_data_frames(rows)

        hours_statistics = Statistics.make_statistics_for_hours(ticker, df)
        days_statistics = Statistics.make_statistics_for_days(ticker, df)

        for st in hours_statistics:
            print(f"{st.get_ticker()} | {st.get_mean_price()} | {st.get_mean_price_changing()} | {st.get_mean_volume()} | {st.get_mean_volume_changing()}")
        print("------------------------------\n\n")

if __name__=="__main__":
    main()