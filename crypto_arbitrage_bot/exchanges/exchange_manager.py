"""
Exchange manager for unified CCXT interface across 6 exchanges.
"""
import ccxt
from typing import Dict
from config.secrets import SecretsManager
from utils.logger import logger

class ExchangeManager:
    def __init__(self):
        self.secrets = SecretsManager()
        self.exchanges = {}
        self.initialize_exchanges()
    
    def initialize_exchanges(self):
        """Initialize CCXT connectors for all 6 exchanges"""
        exchange_configs = {
            "binance": ccxt.binance,
            "kucoin": ccxt.kucoin,
            "mexc": ccxt.mexc,
            "okx": ccxt.okx,
            "gateio": ccxt.gateio,
            "bybit": ccxt.bybit
        }
        
        for name, exchange_class in exchange_configs.items():
            try:
                api_key = self.secrets.get_secret(f"{name}_api_key")
                api_secret = self.secrets.get_secret(f"{name}_api_secret")
                
                if api_key and api_secret:
                    config = {
                        "apiKey": api_key,
                        "secret": api_secret,
                        "enableRateLimit": True,
                        "options": {"defaultType": "spot"}
                    }
                    
                    # KuCoin requires password
                    if name.lower() == "kucoin":
                        password = self.secrets.get_secret(f"{name}_password")
                        if password:
                            config["password"] = password
                        else:
                            logger.warning(f"KuCoin password not found for {name}")
                    
                    self.exchanges[name] = exchange_class(config)
                    logger.info(f"Initialized {name} exchange")
                else:
                    logger.warning(f"API credentials not found for {name}")
            except Exception as e:
                logger.error(f"Failed to initialize {name}: {str(e)}")
    
    def get_balance(self, exchange_name: str) -> Dict:
        """Fetch balance from exchange"""
        try:
            if exchange_name not in self.exchanges:
                return {}
            exchange = self.exchanges[exchange_name]
            return exchange.fetch_balance()
        except Exception as e:
            logger.error(f"Error fetching balance from {exchange_name}: {str(e)}")
            return {}
    
    def get_ticker(self, exchange_name: str, symbol: str) -> Dict:
        """Fetch ticker data"""
        try:
            if exchange_name not in self.exchanges:
                return {}
            exchange = self.exchanges[exchange_name]
            return exchange.fetch_ticker(symbol)
        except Exception as e:
            logger.error(f"Error fetching ticker {symbol} from {exchange_name}: {str(e)}")
            return {}
    
    def create_market_order(self, exchange_name: str, symbol: str, side: str, amount: float) -> Dict:
        """Create a market order"""
        try:
            if exchange_name not in self.exchanges:
                return {"error": "Exchange not initialized"}
            exchange = self.exchanges[exchange_name]
            return exchange.create_market_order(symbol, side, amount)
        except Exception as e:
            logger.error(f"Error creating order on {exchange_name}: {str(e)}")
            return {"error": str(e)}
    
    def get_order_status(self, exchange_name: str, order_id: str, symbol: str) -> Dict:
        """Check order status"""
        try:
            if exchange_name not in self.exchanges:
                return {}
            exchange = self.exchanges[exchange_name]
            return exchange.fetch_order(order_id, symbol)
        except Exception as e:
            logger.error(f"Error fetching order status: {str(e)}")
            return {}
