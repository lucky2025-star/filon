"""
Risk management and circuit breaker logic.
"""
from typing import Dict
from utils.logger import logger
from datetime import datetime, timedelta

class RiskManager:
    def __init__(self, daily_loss_limit: float = -100.0, max_exposure: float = 10.0):
        self.daily_loss_limit = daily_loss_limit
        self.max_exposure = max_exposure
        self.daily_pnl = 0.0
        self.total_exposure = 0.0
        self.failed_trades_count = 0
        self.last_trade_time = None
        self.circuit_breaker_active = False
        self.trade_history = []
    
    def record_trade(self, trade_result: Dict) -> bool:
        """Record a trade and check risk limits"""
        pnl = trade_result.get("pnl", 0)
        self.daily_pnl += pnl
        self.last_trade_time = datetime.now()
        self.trade_history.append({
            "timestamp": datetime.now().isoformat(),
            "pnl": pnl,
            "status": trade_result.get("status", "unknown")
        })
        
        if trade_result.get("status") == "failed":
            self.failed_trades_count += 1
        
        return self.check_risk_limits()
    
    def check_risk_limits(self) -> bool:
        """Check if risk limits are exceeded"""
        if self.daily_pnl <= self.daily_loss_limit:
            logger.warning(f"Daily loss limit reached: {self.daily_pnl}")
            self.circuit_breaker_active = True
            return False
        
        if self.total_exposure > self.max_exposure:
            logger.warning(f"Max exposure exceeded: {self.total_exposure}")
            self.circuit_breaker_active = True
            return False
        
        if self.failed_trades_count > 3:
            logger.warning(f"Too many failed trades: {self.failed_trades_count}")
            self.circuit_breaker_active = True
            return False
        
        self.circuit_breaker_active = False
        return True
    
    def can_trade(self) -> bool:
        """Check if trading is allowed"""
        return not self.circuit_breaker_active
    
    def reset_daily_stats(self) -> None:
        """Reset daily statistics"""
        self.daily_pnl = 0.0
        self.failed_trades_count = 0
        self.trade_history = []
        logger.info("Daily stats reset")
    
    def get_status(self) -> Dict:
        """Get current risk status"""
        return {
            "daily_pnl": self.daily_pnl,
            "total_exposure": self.total_exposure,
            "failed_trades": self.failed_trades_count,
            "circuit_breaker_active": self.circuit_breaker_active,
            "can_trade": self.can_trade()
        }
