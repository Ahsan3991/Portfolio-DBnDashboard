

################### MAIN BODY ########################
import pandas as pd
import os
from extract import extract
from transform import transform
from load import load_to_sql
from logs import log_operation
from datetime import datetime
import sqlite3


def main():
    #extract data
    log_operation("Extracting data")
    companies_df, transactions_df, dividends_df, prices_list = extract()


    log_operation("Data extraction complete")

    #transform data
    log_operation("Transforming data")
    companies_df, transactions_df, dividends_df, prices_list = transform(companies_df, transactions_df, dividends_df, prices_list)
    log_operation("Data transformation complete")

    #load the main tables first
    log_operation("Loading main tables to sql database")
    load_to_sql(companies_df = companies_df, transactions_df = transactions_df, dividends_df = dividends_df)

    log_operation("Data loading complete, Preparing real time prices table")
    #create the realtime prices data frame
    #connect to database


    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/stock_portfolio.db')
    conn = sqlite3.connect(DB_PATH)

    # acquire company ids and ticker symbols from companies table and then merge it with realtime prices dataframe using common ticker symbols
    # just keep the required columns
    company_ids = pd.read_sql("SELECT company_id, ticker_symbol FROM companies;", conn)
    # create realtime_prices dataframe
    realtime_prices_df = pd.DataFrame({
        'ticker_symbol': companies_df['ticker_symbol'].to_list(),
        'share_price': prices_list
    })
    realtime_prices_df = realtime_prices_df.merge(company_ids, on='ticker_symbol', how='inner')
    realtime_prices_df = realtime_prices_df[['company_id', 'share_price']]
    realtime_prices_df['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S') #date format for last updated column

    #load the realtime_price_df to sql
    log_operation("Loading real time prices table")
    load_to_sql(realtime_prices_df = realtime_prices_df)

    print(f"Real time prices dataframe loaded: \n {realtime_prices_df}")
    conn.close()

    log_operation("All tables and respective data loaded successfully, calculating daily unrealized pnl")

    from calculations import compute_daily_unrealized_pnl
    compute_daily_unrealized_pnl(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    unrealized_pnl = pd.read_sql("SELECT * FROM daily_unrealized_pnl;", conn)
    print(unrealized_pnl)


if __name__ == "__main__":
    main()