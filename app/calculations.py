import pandas as pd
import numpy as np
import sqlite3
import os

from load import load_to_sql


def compute_daily_unrealized_pnl(db_path=None):
    if db_path is None:
        print("db_path cannot be None")
        return
    conn = sqlite3.connect(db_path)

    #load transactions table
    transactions_df = pd.read_sql("SELECT company_id, number_of_shares, share_price  FROM transactions", conn)
    print(f"Transactions dataframe loaded: \n {transactions_df}")

    #combine same company transactions to get average buy price
    agg_transactions = transactions_df.groupby('company_id').agg({
        'number_of_shares': 'sum',
        'share_price': lambda x: (transactions_df.loc[x.index, 'number_of_shares'] * x).sum()/
                                    transactions_df.loc[x.index, 'number_of_shares'].sum()
    }).reset_index()
    agg_transactions.rename(columns={'share_price': 'avg_buy_price'}, inplace=True)

    #load realtime prices
    realtime_df = pd.read_sql("SELECT company_id, share_price, last_updated FROM realtime_prices", conn)

    #merge transactions with the latest prices per company
    merged_df = agg_transactions.merge(realtime_df, on='company_id', how='left')
   # print(f"Merged dataframe loaded: \n {merged_df}")

    #compute unrealized P/L
    merged_df['total_investment'] = merged_df['number_of_shares'] * merged_df['avg_buy_price']
    merged_df['current_value'] = merged_df['number_of_shares'] * merged_df['share_price']
    merged_df['unrealized_pnl'] = merged_df['current_value'] - merged_df['total_investment']

    print(f"Merged dataframe loaded: \n {merged_df}")

    conn.close()

    load_to_sql(grouped=merged_df)


