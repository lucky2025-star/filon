"""
Inventory and rebalancing manager.
"""
from typing import Dict, List
from exchanges.exchange_manager import ExchangeManager
from utils.logger import logger

class InventoryManager:
    def __init__(self):
        self.exchange_manager = ExchangeManager()
        self.inventory_snapshots = []
        self.target_allocation = {}
    
    def get_all_balances(self) -> Dict:
        """Fetch balances from all exchanges"""
        all_balances = {}
        for exchange_name in self.exchange_manager.exchanges.keys():
            balances = self.exchange_manager.get_balance(exchange_name)
            all_balances[exchange_name] = balances
        return all_balances
    
    def calculate_drift(self, all_balances: Dict, asset: str) -> Dict:
        """Calculate inventory drift for an asset"""
        drift_analysis = {}
        total_balance = 0
        
        for exchange_name, balances in all_balances.items():
            if asset in balances:
                total_balance += balances[asset].get("free", 0)
        
        ideal_per_exchange = total_balance / len(all_balances)
        
        for exchange_name, balances in all_balances.items():
            if asset in balances:
                actual = balances[asset].get("free", 0)
                drift_pct = ((actual - ideal_per_exchange) / ideal_per_exchange * 100) if ideal_per_exchange > 0 else 0
                drift_analysis[exchange_name] = {
                    "actual": actual,
                    "ideal": ideal_per_exchange,
                    "drift_pct": drift_pct,
                    "status": "excess" if drift_pct > 10 else ("deficit" if drift_pct < -10 else "balanced")
                }
        
        return drift_analysis
    
    def suggest_rebalancing(self, all_balances: Dict, assets: List[str]) -> List[Dict]:
        """Suggest rebalancing trades"""
        suggestions = []
        
        for asset in assets:
            drift = self.calculate_drift(all_balances, asset)
            
            for exchange_name, data in drift.items():
                if data["status"] == "excess":
                    suggestions.append({
                        "action": "sell",
                        "exchange": exchange_name,
                        "asset": asset,
                        "amount": data["actual"] - data["ideal"],
                        "reason": "excess inventory"
                    })
                elif data["status"] == "deficit":
                    suggestions.append({
                        "action": "buy",
                        "exchange": exchange_name,
                        "asset": asset,
                        "amount": data["ideal"] - data["actual"],
                        "reason": "insufficient inventory"
                    })
        
        return suggestions
    
    def get_portfolio_value(self, all_balances: Dict, prices: Dict) -> float:
        """Calculate total portfolio value in USD"""
        total_value = 0
        
        for exchange_name, balances in all_balances.items():
            for asset, data in balances.items():
                amount = data.get("free", 0)
                if amount > 0:
                    symbol = f"{asset}/USDT"
                    if symbol in prices and exchange_name in prices[symbol]:
                        price = prices[symbol][exchange_name].get("last", 0)
                        total_value += amount * price
        
        return total_value
