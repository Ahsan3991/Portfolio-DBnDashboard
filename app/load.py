

################### LOAD OPERATION ########################

def load_to_sql(companies_df = None, transactions_df = None, dividends_df = None, realtime_prices_df = None, grouped=None):
    import os
    import pandas as pd
    import sqlite3

    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/stock_portfolio.db')
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    #create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY,
    company_name TEXT UNIQUE,
    sector TEXT,
    ticker_symbol TEXT UNIQUE
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    transaction_date TEXT,
    number_of_shares INTEGER,
    share_price REAL NOT NULL,
    sales_tax REAL,
    commission_tax REAL,
    cdc_charges REAL,
    FOREIGN KEY (company_id) REFERENCES companies (company_id) ON DELETE CASCADE
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dividends (
    dividend_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    dividend_date TEXT,
    payout_ratio REAL NOT NULL,
    cgt_tax REAL,
    net_dividend_payout REAL NOT NULL,
    FOREIGN KEY (company_id) REFERENCES companies (company_id) ON DELETE CASCADE
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS realtime_prices (
    price_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    share_price REAL NOT NULL,
    last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies (company_id)
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_unrealized_pnl (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    number_of_shares TEXT,
    avg_buy_price INTEGER,
    share_price REAL NOT NULL,
    last_updated DATETIME NOT NULL,
    total_investment REAL,
    current_value REAL NOT NULL,
    unrealized_pnl REAL NOT NULL,
    FOREIGN KEY (company_id) REFERENCES companies (company_id)
    );
    ''')

    #load csv to tables
    if companies_df is not None:
        existing_ids = pd.read_sql("SELECT company_id FROM companies", conn)['company_id']
        companies_df = companies_df[~companies_df['company_id'].isin(existing_ids)]
        companies_df.to_sql('companies', conn, if_exists='append', index=False) #static master data should not duplicate
    if transactions_df is not None:
        transactions_df.to_sql('transactions', conn, if_exists='replace', index=False) #
    if dividends_df is not None:
        dividends_df.to_sql('dividends', conn, if_exists='replace', index=False)
    if realtime_prices_df is not None:
        realtime_prices_df.to_sql('realtime_prices', conn, if_exists='replace', index=False) #only need the latest prices table
    if grouped is not None:
        grouped.to_sql('daily_unrealized_pnl', conn, if_exists='append', index=False) #keeps latest and historic values

    conn.commit()
    conn.close()

