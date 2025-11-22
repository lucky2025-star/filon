"""
Helper utilities for the arbitrage bot.
"""
from datetime import datetime
from typing import Dict, List

def format_price(price: float, decimals: int = 2) -> str:
    """Format price with decimals"""
    return f"{price:,.{decimals}f}"

def format_percentage(percentage: float, decimals: int = 2) -> str:
    """Format percentage"""
    return f"{percentage:.{decimals}f}%"

def calculate_roi(profit: float, investment: float) -> float:
    """Calculate ROI"""
    if investment <= 0:
        return 0
    return (profit / investment) * 100

def get_timestamp() -> str:
    """Get current timestamp"""
    return datetime.now().isoformat()

def parse_symbol(symbol: str) -> tuple:
    """Parse symbol into base and quote"""
    parts = symbol.split("/")
    if len(parts) == 2:
        return parts[0], parts[1]
    return None, None

def filter_dict(data: Dict, keys: List[str]) -> Dict:
    """Filter dictionary to only include specified keys"""
    return {k: v for k, v in data.items() if k in keys}
