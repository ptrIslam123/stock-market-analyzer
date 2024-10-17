from stock_info import *
from global_configuration import INTRADAY_STOCK_MARKET_INFO_TABLE_PATH

from_date = '2024-10-14'
to_date = ''
ticker="ASTR"

def main():
    conn = sqlite3.connect(INTRADAY_STOCK_MARKET_INFO_TABLE_PATH)
    cursor = conn.cursor()


if __name__=="__main__":
    main()