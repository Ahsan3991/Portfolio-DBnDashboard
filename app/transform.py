
################### TRANSFORM OPERATION ########################

def transform(companies_df, transactions_df, dividends_df, prices_list):

    #Clean numeric data
    transactions_df['share_price'] = transactions_df['share_price'].replace(',','',regex=True).astype(float)
    transactions_df['sales_tax'] = transactions_df['sales_tax'].replace(',','',regex=True).astype(float).fillna(0)
    transactions_df['cdc_charges'] = transactions_df['cdc_charges'].replace(',', '', regex=True).astype(float).fillna(0)
    transactions_df['commission_tax'] = transactions_df['commission_tax'].replace(',', '', regex=True).astype(float).fillna(0)

    dividends_df['payout_ratio'] = dividends_df['payout_ratio'].replace(',', '', regex=True).astype(float)
    dividends_df['cgt_tax'] = dividends_df['cgt_tax'].replace(',', '', regex=True).astype(float)
    dividends_df['net_dividend_payout'] = dividends_df['net_dividend_payout'].replace(',', '', regex=True).astype(float)
    
    #clean the real time prices extracted from web scraping
    transformed_prices = []
    for price in prices_list:
        clean_price = price.replace(',','').replace("Rs.",'').strip()
        clean_price = float(clean_price)
        transformed_prices.append(clean_price)




    return companies_df, transactions_df, dividends_df, transformed_prices
