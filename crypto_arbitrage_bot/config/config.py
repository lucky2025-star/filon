"""
Configuration loader and manager for the arbitrage bot.
Handles loading settings from environment variables and config files.
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings"""
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    EXCHANGES = ["binance", "kucoin", "mexc", "okx", "gateio", "bybit"]
    MIN_SPREAD_THRESHOLD = float(os.getenv("MIN_SPREAD_THRESHOLD", "0.3"))
    MAX_POSITION_SIZE = float(os.getenv("MAX_POSITION_SIZE", "1.0"))
    MAX_CONCURRENT_TRADES = int(os.getenv("MAX_CONCURRENT_TRADES", "3"))
    RE_ENTRY_DELAY = int(os.getenv("RE_ENTRY_DELAY", "5"))
    DAILY_LOSS_LIMIT = float(os.getenv("DAILY_LOSS_LIMIT", "-100.0"))
    MAX_TOTAL_EXPOSURE = float(os.getenv("MAX_TOTAL_EXPOSURE", "10.0"))
    PRICE_UPDATE_INTERVAL = int(os.getenv("PRICE_UPDATE_INTERVAL", "2"))
    BALANCE_UPDATE_INTERVAL = int(os.getenv("BALANCE_UPDATE_INTERVAL", "30"))

settings = Settings()
