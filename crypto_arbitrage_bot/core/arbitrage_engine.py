"""
Core arbitrage calculation engine.
"""
from typing import Dict, List
from utils.logger import logger

class ArbitrageEngine:
    def __init__(self, min_spread: float = 0.3, max_position_size: float = 1.0):
        self.min_spread = min_spread
        self.max_position_size = max_position_size
        self.active_trades = []
    
    def calculate_profit(self, buy_price: float, sell_price: float, quantity: float,
                        buy_fee: float = 0.001, sell_fee: float = 0.001) -> Dict:
        """Calculate profit for an arbitrage trade"""
        if quantity <= 0 or buy_price <= 0:
            return {"error": "Invalid inputs"}
        
        buy_cost = buy_price * quantity
        buy_fee_cost = buy_cost * buy_fee
        total_buy_cost = buy_cost + buy_fee_cost
        
        sell_revenue = sell_price * quantity
        sell_fee_cost = sell_revenue * sell_fee
        net_revenue = sell_revenue - sell_fee_cost
        
        profit_usd = net_revenue - total_buy_cost
        profit_pct = (profit_usd / total_buy_cost) * 100
        
        return {
            "buy_cost": buy_cost,
            "buy_fee": buy_fee_cost,
            "total_buy_cost": total_buy_cost,
            "sell_revenue": sell_revenue,
            "sell_fee": sell_fee_cost,
            "net_revenue": net_revenue,
            "profit_usd": profit_usd,
            "profit_pct": profit_pct
        }
    
    def rank_opportunities(self, opportunities: List[Dict]) -> List[Dict]:
        """Rank opportunities by profitability"""
        ranked = []
        for opp in opportunities:
            if opp["spread_pct"] >= self.min_spread:
                ranked.append(opp)
        return sorted(ranked, key=lambda x: x["spread_pct"], reverse=True)
    
    def filter_by_liquidity(self, opportunities: List[Dict], min_volume: float = 0.1) -> List[Dict]:
        """Filter opportunities by minimum liquidity"""
        return opportunities
    
    def validate_trade(self, opportunity: Dict, available_funds: Dict) -> bool:
        """Validate if trade can be executed"""
        buy_exchange = opportunity["buy_exchange"]
        symbol = opportunity["symbol"]
        base_asset = symbol.split("/")[0]
        
        if buy_exchange not in available_funds:
            return False
        
        if base_asset not in available_funds[buy_exchange]:
            return False
        
        return True
