"""
Main entry point for the arbitrage bot.
"""
import sys
import asyncio
from utils.logger import logger
from config.config import settings
from core.price_monitor import PriceMonitor
from core.arbitrage_engine import ArbitrageEngine
from core.trade_executor import TradeExecutor
from core.inventory_manager import InventoryManager
from core.risk_manager import RiskManager
from database.db import init_db
from utils.notifications import TelegramNotifier

class ArbitrageBot:
    def __init__(self):
        self.price_monitor = PriceMonitor()
        self.arbitrage_engine = ArbitrageEngine(
            min_spread=settings.MIN_SPREAD_THRESHOLD,
            max_position_size=settings.MAX_POSITION_SIZE
        )
        self.trade_executor = TradeExecutor()
        self.inventory_manager = InventoryManager()
        self.risk_manager = RiskManager(
            daily_loss_limit=settings.DAILY_LOSS_LIMIT,
            max_exposure=settings.MAX_TOTAL_EXPOSURE
        )
        self.telegram_notifier = TelegramNotifier()
        self.auto_trading_enabled = False
        self.trading_pairs = ["BTC/USDT", "ETH/USDT"]
    
    def start(self):
        """Start the bot"""
        logger.info("Starting arbitrage bot...")
        init_db()
        self.monitoring_loop()
    
    def monitoring_loop(self):
        """Main monitoring and trading loop"""
        while True:
            try:
                prices = self.price_monitor.fetch_prices(self.trading_pairs)
                opportunities = self.price_monitor.detect_opportunities(
                    prices, 
                    min_spread=settings.MIN_SPREAD_THRESHOLD
                )
                
                logger.info(f"Detected {len(opportunities)} opportunities")
                
                if opportunities and self.auto_trading_enabled and self.risk_manager.can_trade():
                    for opp in opportunities[:1]:  # Execute top opportunity
                        self.execute_opportunity(opp)
                
                asyncio.sleep(settings.PRICE_UPDATE_INTERVAL)
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                asyncio.sleep(5)
    
    def execute_opportunity(self, opportunity: dict):
        """Execute an arbitrage opportunity"""
        logger.info(f"Executing opportunity: {opportunity['symbol']} {opportunity['buy_exchange']} -> {opportunity['sell_exchange']}")
        
        trade_result = self.trade_executor.execute_arbitrage_trade(
            opportunity["buy_exchange"],
            opportunity["sell_exchange"],
            opportunity["symbol"],
            0.01  # Fixed small amount for testing
        )
        
        if trade_result["status"] == "completed":
            logger.info(f"Trade executed successfully: {trade_result['trade_id']}")
            msg = f"✅ Trade executed: {opportunity['symbol']} spread {opportunity['spread_pct']:.2f}%"
            self.telegram_notifier.send_message("1395251148", msg)

def main():
    """Main entry point"""
    try:
        bot = ArbitrageBot()
        bot.start()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
