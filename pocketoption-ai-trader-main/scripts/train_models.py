import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import joblib
import os
from src.data_engine import DataEngine

def create_features(df):
    # Add technical indicators
    df['returns'] = df['close'].pct_change()
    df['volatility'] = df['close'].rolling(20).std()
    df['rsi'] = 100 - (100 / (1 + df['close'].rolling(14).mean() / df['close'].rolling(14).std()))
    df['macd'] = df['close'].ewm(span=12).mean() - df['close'].ewm(span=26).mean()
    df.dropna(inplace=True)
    
    # Create labels (1 = buy, 0 = sell)
    df['label'] = np.where(df['returns'].shift(-1) > 0, 1, 0)
    return df[['rsi', 'macd', 'volatility']], df['label']

def train_model(X, y, pair):
    # Train classifier
    clf = GradientBoostingClassifier(n_estimators=200, learning_rate=0.1)
    clf.fit(X, y)
    joblib.dump(clf, f'models/production/{pair.replace("/", "_")}_clf.pkl')
    
    # Train LSTM
    X_seq = X.values.reshape((X.shape[0], 1, X.shape[1]))
    model = Sequential([
        LSTM(64, input_shape=(1, X.shape[1])),
        Dense(1, activation='sigmoid')
    ])
    model.compile(loss='binary_crossentropy', optimizer='adam')
    model.fit(X_seq, y, epochs=50, batch_size=32, verbose=0)
    model.save(f'models/production/{pair.replace("/", "_")}_lstm.h5')

if __name__ == "__main__":
    engine = DataEngine()
    for pair in config.TRADING_PAIRS:
        print(f"Training models for {pair}")
        try:
            df = pd.read_csv(f'data/historical/{pair.replace("/", "_")}.csv')
            X, y = create_features(df)
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
            train_model(X_train, y_train, pair)
        except Exception as e:
            print(f"Error training {pair}: {str(e)}")
