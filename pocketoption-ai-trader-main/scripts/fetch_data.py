import os
import pandas as pd
from alpha_vantage.foreignexchange import ForeignExchange
from src.data_engine import DataEngine
import time

def fetch_historical_data():
    av = ForeignExchange(key=os.getenv('ALPHA_VANTAGE_KEY'))
    engine = DataEngine()
    
    for pair in config.TRADING_PAIRS:
        symbol = pair.replace('/', '')
        print(f"Fetching data for {symbol}")
        
        try:
            # Get daily data for 1 year
            data, _ = av.get_currency_exchange_daily(
                from_symbol=pair.split('/')[0],
                to_symbol=pair.split('/')[1],
                outputsize='full'
            )
            df = pd.DataFrame(data).T
            df.columns = ['open', 'high', 'low', 'close']
            df.to_csv(f'data/historical/{symbol}.csv')
            time.sleep(15)  # API rate limit
        except Exception as e:
            print(f"Error fetching {pair}: {str(e)}")

if __name__ == "__main__":
    fetch_historical_data()
