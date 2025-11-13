class RiskManager:
    def __init__(self, initial_balance=1000):
        self.balance = initial_balance
        self.daily_profit = 0
        self.daily_loss = 0
        self.trade_count = 0
        self.last_trade_time = 0
        
    def calculate_size(self, confidence):
        """Calculate position size based on confidence and balance"""
        base_size = min(config.BASE_AMOUNT, self.balance * 0.02)
        return base_size * confidence  # Scale with confidence
        
    def can_trade(self):
        """Check if trading is allowed"""
        # Rate limiting
        if time.time() - self.last_trade_time < 60:
            return False
            
        # Daily loss limit
        if self.daily_loss > self.balance * config.MAX_DAILY_LOSS:
            return False
            
        # Trade count limit
        if self.trade_count >= config.MAX_TRADES_PER_HOUR:
            return False
            
        return True
        
    def update_balance(self, profit):
        """Update after trade completion"""
        self.balance += profit
        self.trade_count += 1
        self.last_trade_time = time.time()
        
        if profit > 0:
            self.daily_profit += profit
        else:
            self.daily_loss += abs(profit)
            
        # Reset counters daily
        if datetime.now().hour == 0:
            self.daily_profit = 0
            self.daily_loss = 0
            self.trade_count = 0
