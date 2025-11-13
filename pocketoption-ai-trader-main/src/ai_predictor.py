import joblib
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from .data_engine import DataEngine

class AIPredictor:
    def __init__(self):
        self.engine = DataEngine()
        self.models = self.load_models()
        
    def load_models(self):
        models = {}
        for pair in config.TRADING_PAIRS:
            pair_key = pair.replace('/', '_')
            try:
                models[pair] = {
                    'clf': joblib.load(f'models/production/{pair_key}_clf.pkl'),
                    'lstm': load_model(f'models/production/{pair_key}_lstm.h5')
                }
            except:
                models[pair] = None
        return models
        
    def generate_signal(self, pair):
        if not self.models.get(pair):
            return ('HOLD', 0)
            
        df = self.engine.get_realtime_data(pair)
        if len(df) < 30:
            return ('HOLD', 0)
            
        # Prepare features
        features = self.prepare_features(df)
        
        # Get predictions
        clf_pred = self.models[pair]['clf'].predict_proba([features])[0][1]
        lstm_pred = self.models[pair]['lstm'].predict(np.array([features]).reshape(1, 1, -1))[0][0]
        
        # Combine with sentiment
        sentiment = self.engine.get_news_sentiment(pair)
        confidence = (clf_pred * 0.4 + lstm_pred * 0.4 + sentiment * 0.2)
        
        if confidence > config.MIN_CONFIDENCE:
            return ('BUY', confidence) if clf_pred > 0.5 else ('SELL', confidence)
        return ('HOLD', 0)
        
    def prepare_features(self, df):
        # Calculate technical indicators
        df['returns'] = df['close'].pct_change()
        df['volatility'] = df['close'].rolling(20).std()
        df['rsi'] = 100 - (100 / (1 + df['close'].rolling(14).mean() / df['close'].rolling(14).std()))
        df['macd'] = df['close'].ewm(span=12).mean() - df['close'].ewm(span=26).mean()
        last = df.iloc[-1]
        return [last['rsi'], last['macd'], last['volatility']]
