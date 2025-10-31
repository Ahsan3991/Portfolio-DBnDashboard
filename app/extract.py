import asyncio

################### EXTRACT OPERATION ########################

def extract():

    import os
    import pandas as pd


    #Paths -- relative to this script's directory
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, '../data')

    #Get CSV paths
    companies_csv = os.path.join(DATA_DIR, 'companies.csv')
    dividends_csv = os.path.join(DATA_DIR, 'dividends.csv')
    transactions_csv = os.path.join(DATA_DIR, 'transactions.csv')

    #reading CSVs
    companies_df = pd.read_csv(companies_csv, header=None, skipinitialspace=True)
    dividends_df = pd.read_csv(dividends_csv, header=None, skipinitialspace=True)
    transactions_df = pd.read_csv(transactions_csv, header=None, skipinitialspace=True)

    #Set correct column names
    companies_df.columns = ['company_id', 'company_name', 'sector', 'ticker_symbol']
    dividends_df.columns=['company_id', 'dividend_date', 'payout_ratio', 'cgt_tax', 'net_dividend_payout']
    transactions_df.columns=['company_id', 'transaction_date', 'number_of_shares', 'share_price', 'sales_tax', 'commission_tax', 'cdc_charges']

    ticker_symbols = companies_df['ticker_symbol'].tolist()
    realtime_prices = asyncio.run(extract_realtime_prices(ticker_symbols))


    return companies_df, transactions_df, dividends_df, realtime_prices



async def extract_realtime_prices(ticker_sym_lists):
    #import requests
    #from bs4 import BeautifulSoup
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout


    realtime_prices = []

    async def fetch_one_price(browser, symbol):
        page = await browser.new_page()
        try:
            url= f"https://dps.psx.com.pk/company/{symbol}"
            print(url)
            await page.goto(url, timeout=120000)
            await page.wait_for_selector('div.quote__close', timeout=120000)
            price =await page.locator('div.quote__close').text_content()
            print(f"{symbol} price: {price}")
            return price.strip()
        except PlaywrightTimeout as e:
            print(f"Timeout error for {symbol}:", e)
            realtime_prices.append(None)
        except Exception as e:
            print(f"{symbol} error: {e}")
            return None
        finally:
            await page.close()

    async with async_playwright() as playwright:
        #start new browser page
        browser = await playwright.chromium.launch(headless=True)

        #create tasks
        tasks = [fetch_one_price(browser, symbol) for symbol in ticker_sym_lists]

        #gather all prices in order of ticker symbol lists
        realtime_prices = await asyncio.gather(*tasks)

        await browser.close()

    return list(realtime_prices) #returning the list of realtime prices


