import pandas as pd
from datetime import datetime

class PerformanceTracker:
    def __init__(self):
        self.trades = pd.DataFrame(columns=[
            'timestamp', 'pair', 'direction', 'confidence',
            'amount', 'profit', 'success'
        ])
        self.starting_balance = 1000
        self.current_balance = self.starting_balance
        
    def record_trade(self, trade):
        self.trades = self.trades.append(trade, ignore_index=True)
        self.current_balance += trade.get('profit', 0)
        
    def daily_report(self):
        today = datetime.now().date()
        daily_trades = self.trades[self.trades['timestamp'].dt.date == today]
        
        if len(daily_trades) == 0:
            return "No trades today"
            
        win_rate = len(daily_trades[daily_trades['success']]) / len(daily_trades)
        profit = daily_trades['profit'].sum()
        roi = (self.current_balance - self.starting_balance) / self.starting_balance
        
        return f"""
📊 Daily Performance Report
════════════════════════════
• Trades: {len(daily_trades)}
• Win Rate: {win_rate:.1%}
• Profit: ${profit:.2f}
• Balance: ${self.current_balance:.2f}
• ROI: {roi:.1%}
════════════════════════════
"""
