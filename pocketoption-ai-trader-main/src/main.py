import time
import yaml
from .trading_bot import TradingBot
from .health_check import start_health_server

# Load configuration
with open('config/api_keys.yaml') as f:
    api_keys = yaml.safe_load(f)

with open('config/settings.yaml') as f:
    settings = yaml.safe_load(f)

# Set global config
class Config:
    TRADING_PAIRS = settings['trading']['pairs']
    TELEGRAM_TOKEN = api_keys['telegram']['token']
    TELEGRAM_CHANNEL = api_keys['telegram']['channel_id']
    POCKET_OPTION_TOKEN = api_keys['pocket_option']['token']
    BASE_AMOUNT = settings['trading']['base_amount']

if __name__ == "__main__":
    # Start health check server
    start_health_server()
    
    # Initialize and run bot
    bot = TradingBot()
    print("Starting AI Trading Bot...")
    
    try:
        while True:
            bot.run_cycle()
            time.sleep(15)  # Run every 15 seconds
    except KeyboardInterrupt:
        print("Bot stopped by user")
    except Exception as e:
        bot.telegram.send_alert(f"🆘 CRITICAL ERROR: {str(e)}")
        raise
