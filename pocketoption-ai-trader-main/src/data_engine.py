import pandas as pd
import requests
import yfinance as yf
from bs4 import BeautifulSoup
import time
import os

class DataEngine:
    def __init__(self):
        self.cache = {}
        
    def get_realtime_data(self, pair):
        """Get 1-minute OHLCV data"""
        if pair in self.cache:
            return self.cache[pair]
            
        symbol = pair.replace('/', '')
        try:
            # Try Alpha Vantage first
            url = f"https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol={pair[:3]}&to_symbol={pair[4:]}&interval=1min&apikey={os.getenv('ALPHA_VANTAGE_KEY')}"
            data = requests.get(url).json()
            df = pd.DataFrame(data['Time Series FX (1min)']).T
            df = df.rename(columns={
                '1. open': 'open',
                '2. high': 'high',
                '3. low': 'low',
                '4. close': 'close'
            }).astype(float)
            self.cache[pair] = df
            return df
        except:
            # Fallback to Yahoo Finance
            df = yf.download(tickers=symbol, period='1d', interval='1m')
            self.cache[pair] = df
            return df
            
    def get_news_sentiment(self, pair):
        """Get market sentiment score (-1 to 1)"""
        base, quote = pair.split('/')
        try:
            # Use NewsAPI
            url = f"https://newsapi.org/v2/everything?q={base}+{quote}&apiKey={os.getenv('NEWSAPI_KEY')}"
            articles = requests.get(url).json().get('articles', [])
            headlines = ' '.join([a['title'] for a in articles[:5]])
            
            # Simple sentiment analysis
            positive_words = ['bullish', 'up', 'strong', 'buy', 'growth']
            negative_words = ['bearish', 'down', 'weak', 'sell', 'drop']
            
            score = 0
            for word in positive_words:
                if word in headlines.lower():
                    score += 0.2
            for word in negative_words:
                if word in headlines.lower():
                    score -= 0.2
                    
            return max(-1, min(1, score))
        except:
            return 0  # Neutral on error
