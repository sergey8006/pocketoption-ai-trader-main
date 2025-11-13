import time
from datetime import datetime
from .ai_predictor import AIPredictor
from .risk_manager import RiskManager
from .performance import PerformanceTracker
from .telegram_bot import TelegramBot
from .pocket_api import PocketOptionAPI

class TradingBot:
    def __init__(self, backtest=False):
        self.ai = AIPredictor()
        self.risk = RiskManager()
        self.performance = PerformanceTracker()
        self.telegram = TelegramBot()
        self.api = PocketOptionAPI(config.POCKET_OPTION_TOKEN) if not backtest else None
        self.active_trades = {}
        
    def run_cycle(self):
        for pair in config.TRADING_PAIRS:
            signal, confidence = self.ai.generate_signal(pair)
            
            if signal != 'HOLD' and self.risk.can_trade():
                amount = self.risk.calculate_size(confidence)
                if not backtest:
                    self.execute_trade(pair, signal, amount, confidence)
                else:
                    # Simulate in backtest
                    self.performance.record_trade({
                        'timestamp': datetime.now(),
                        'pair': pair,
                        'direction': signal,
                        'confidence': confidence,
                        'amount': amount,
                        'profit': amount * 0.92 if confidence > 0.7 else -amount,
                        'success': confidence > 0.7
                    })
        
        # Check trade results
        self.check_trade_results()
        
        # Daily report
        if datetime.now().strftime('%H:%M') == config.REPORT_TIME:
            self.telegram.send_report(self.performance.daily_report())
    
    def execute_trade(self, pair, direction, amount, confidence):
        try:
            # Execute via Pocket Option API
            result = self.api.place_trade(
                pair=pair,
                amount=amount,
                direction=direction,
                duration=1  # 1-minute trade
            )
            
            if result['success']:
                trade_id = result['data']['id']
                self.active_trades[trade_id] = {
                    'pair': pair,
                    'direction': direction,
                    'confidence': confidence,
                    'amount': amount,
                    'open_time': time.time()
                }
                self.telegram.send_trade_alert(pair, direction, confidence, amount)
        except Exception as e:
            self.telegram.send_alert(f"Trade Error: {str(e)}")
    
    def check_trade_results(self):
        current_time = time.time()
        completed = []
        
        for trade_id, trade in list(self.active_trades.items()):
            if current_time - trade['open_time'] > 70:  # 1m + 10s buffer
                result = self.api.get_trade_result(trade_id)
                if result:
                    trade['profit'] = result['profit']
                    trade['success'] = result['profit'] > 0
                    self.performance.record_trade(trade)
                    self.risk.update_balance(trade['profit'])
                    completed.append(trade_id)
        
        # Remove completed trades
        for trade_id in completed:
            del self.active_trades[trade_id]
