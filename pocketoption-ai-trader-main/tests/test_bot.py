import pytest
from src.trading_bot import TradingBot
from unittest.mock import MagicMock

def test_trade_execution():
    bot = TradingBot()
    bot.ai.generate_signal = MagicMock(return_value=('BUY', 0.92))
    bot.risk.can_trade = MagicMock(return_value=True)
    bot.execute_trade = MagicMock()
    
    bot.run_cycle()
    bot.execute_trade.assert_called_once()

def test_risk_management():
    bot = TradingBot()
    bot.risk.daily_loss = 100  # Simulate loss
    bot.risk.balance = 1000
    bot.risk.max_daily_loss = 0.05  # 5%
    
    # Should not trade when over daily loss limit
    assert not bot.risk.can_trade()
    
    # Reset daily loss
    bot.risk.daily_loss = 0
    assert bot.risk.can_trade()
