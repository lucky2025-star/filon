"""
Real-time price monitoring across exchanges.
"""
from typing import Dict, List
from exchanges.exchange_manager import ExchangeManager
from utils.logger import logger
import time

class PriceMonitor:
    def __init__(self):
        self.exchange_manager = ExchangeManager()
        self.price_cache = {}
        self.last_update = {}
        self.update_interval = 2  # seconds
    
    def fetch_prices(self, symbols: List[str]) -> Dict:
        """Fetch prices from all exchanges for given symbols"""
        prices = {}
        
        for symbol in symbols:
            prices[symbol] = {}
            for exchange_name in self.exchange_manager.exchanges.keys():
                ticker = self.exchange_manager.get_ticker(exchange_name, symbol)
                if ticker:
                    prices[symbol][exchange_name] = {
                        "bid": ticker.get("bid", 0),
                        "ask": ticker.get("ask", 0),
                        "last": ticker.get("last", 0),
                        "timestamp": ticker.get("timestamp", time.time())
                    }
        
        self.price_cache = prices
        self.last_update[str(symbols)] = time.time()
        return prices
    
    def get_cached_prices(self, symbols: List[str]) -> Dict:
        """Get cached prices if available"""
        return self.price_cache
    
    def calculate_spread(self, buy_exchange: str, sell_exchange: str, 
                        buy_price: float, sell_price: float,
                        buy_fee: float = 0.001, sell_fee: float = 0.001) -> float:
        """Calculate net spread percentage"""
        if buy_price <= 0:
            return 0
        spread = ((sell_price - buy_price) / buy_price) * 100 - (buy_fee * 100) - (sell_fee * 100)
        return spread
    
    def detect_opportunities(self, prices: Dict, min_spread: float = 0.3) -> List[Dict]:
        """Detect arbitrage opportunities"""
        opportunities = []
        exchanges = list(self.exchange_manager.exchanges.keys())
        
        for symbol, exchange_data in prices.items():
            for buy_ex in exchanges:
                for sell_ex in exchanges:
                    if buy_ex == sell_ex:
                        continue
                    
                    if buy_ex not in exchange_data or sell_ex not in exchange_data:
                        continue
                    
                    buy_ask = exchange_data[buy_ex].get("ask", 0)
                    sell_bid = exchange_data[sell_ex].get("bid", 0)
                    
                    if buy_ask <= 0 or sell_bid <= 0:
                        continue
                    
                    spread = self.calculate_spread(buy_ex, sell_ex, buy_ask, sell_bid)
                    
                    if spread >= min_spread:
                        opportunities.append({
                            "symbol": symbol,
                            "buy_exchange": buy_ex,
                            "sell_exchange": sell_ex,
                            "buy_price": buy_ask,
                            "sell_price": sell_bid,
                            "spread_pct": spread
                        })
        
        return sorted(opportunities, key=lambda x: x["spread_pct"], reverse=True)[:10]
