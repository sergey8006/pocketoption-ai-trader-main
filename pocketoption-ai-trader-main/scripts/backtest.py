import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.trading_bot import TradingBot
from src.performance import PerformanceTracker
import argparse

def run_backtest(days=30):
    tracker = PerformanceTracker()
    bot = TradingBot(backtest=True)
    start_date = datetime.now() - timedelta(days=days)
    
    print(f"Running backtest for {days} days...")
    for i in range(days * 24 * 60):  # Minute intervals
        current_time = start_date + timedelta(minutes=i)
        if current_time.hour < 1 or current_time.hour > 22:  # Skip off-hours
            continue
            
        for pair in config.TRADING_PAIRS:
            signal = bot.generate_signal(pair, current_time)
            if signal[0] != 'HOLD':
                # Simulate trade outcome
                outcome = np.random.choice(
                    [True, False], 
                    p=[signal[1], 1-signal[1]])  # Confidence-based outcome
                profit = config.BASE_AMOUNT * 0.92 if outcome else -config.BASE_AMOUNT
                tracker.record_trade({
                    'timestamp': current_time,
                    'pair': pair,
                    'direction': signal[0],
                    'confidence': signal[1],
                    'amount': config.BASE_AMOUNT,
                    'profit': profit,
                    'success': outcome
                })
    
    return tracker.daily_report()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=7)
    args = parser.parse_args()
    
    report = run_backtest(args.days)
    print(report)
