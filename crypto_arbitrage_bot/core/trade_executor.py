"""
Trade execution module for placing and monitoring orders.
"""
from typing import Dict
from exchanges.exchange_manager import ExchangeManager
from utils.logger import logger
from datetime import datetime

class TradeExecutor:
    def __init__(self):
        self.exchange_manager = ExchangeManager()
        self.trade_history = []
        self.active_orders = {}
    
    def execute_arbitrage_trade(self, buy_exchange: str, sell_exchange: str,
                               symbol: str, quantity: float) -> Dict:
        """Execute buy and sell orders for arbitrage"""
        trade_id = f"{datetime.now().timestamp()}"
        trade_record = {
            "trade_id": trade_id,
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "quantity": quantity,
            "buy_exchange": buy_exchange,
            "sell_exchange": sell_exchange,
            "buy_order": None,
            "sell_order": None,
            "status": "pending",
            "error": None
        }
        
        buy_result = self.exchange_manager.create_market_order(
            buy_exchange, symbol, "buy", quantity
        )
        
        if "error" in buy_result:
            trade_record["error"] = f"Buy failed: {buy_result['error']}"
            trade_record["status"] = "failed"
            self.trade_history.append(trade_record)
            logger.error(f"Buy order failed: {buy_result['error']}")
            return trade_record
        
        trade_record["buy_order"] = buy_result
        
        sell_result = self.exchange_manager.create_market_order(
            sell_exchange, symbol, "sell", quantity
        )
        
        if "error" in sell_result:
            trade_record["error"] = f"Sell failed: {sell_result['error']}"
            trade_record["status"] = "partial"
            logger.error(f"Sell order failed: {sell_result['error']}")
        else:
            trade_record["sell_order"] = sell_result
            trade_record["status"] = "completed"
        
        self.trade_history.append(trade_record)
        return trade_record
    
    def get_order_status(self, exchange_name: str, order_id: str, symbol: str) -> Dict:
        """Check status of an order"""
        return self.exchange_manager.get_order_status(exchange_name, order_id, symbol)
    
    def cancel_order(self, exchange_name: str, order_id: str, symbol: str) -> Dict:
        """Cancel an open order"""
        try:
            exchange = self.exchange_manager.exchanges.get(exchange_name)
            if not exchange:
                return {"error": "Exchange not found"}
            return exchange.cancel_order(order_id, symbol)
        except Exception as e:
            logger.error(f"Error canceling order: {str(e)}")
            return {"error": str(e)}
    
    def get_trade_history(self, limit: int = 20) -> list:
        """Get recent trade history"""
        return self.trade_history[-limit:]
    
    def calculate_pnl(self, trade_record: Dict) -> float:
        """Calculate profit/loss for a trade"""
        if not trade_record.get("buy_order") or not trade_record.get("sell_order"):
            return 0.0
        
        buy_cost = trade_record["quantity"] * trade_record["buy_order"].get("average", 0)
        sell_revenue = trade_record["quantity"] * trade_record["sell_order"].get("average", 0)
        
        return sell_revenue - buy_cost
