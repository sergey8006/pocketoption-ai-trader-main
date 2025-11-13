import requests

class PocketOptionAPI:
    BASE_URL = "https://api.pocketoption.com"
    
    def __init__(self, api_token):
        self.token = api_token
        
    def place_trade(self, pair, amount, direction, duration):
        payload = {
            "symbol": pair.replace("/", ""),
            "amount": amount,
            "timeframe": duration,
            "direction": direction.lower(),
            "token": self.token
        }
        response = requests.post(f"{self.BASE_URL}/api/trade", json=payload)
        return response.json()
        
    def get_trade_result(self, trade_id):
        response = requests.get(f"{self.BASE_URL}/api/history/{trade_id}")
        return response.json().get('data')
        
    def get_balance(self):
        response = requests.get(f"{self.BASE_URL}/api/account?token={self.token}")
        return response.json().get('balance', 0)
