"""
Database connection and operations.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, Trade, Balance, DailyStats
from datetime import datetime

DATABASE_URL = "sqlite:///./arbitrage_bot.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def save_trade(trade_data: dict):
    """Save a trade to database"""
    db = SessionLocal()
    try:
        trade = Trade(
            trade_id=trade_data.get("trade_id"),
            symbol=trade_data.get("symbol"),
            quantity=trade_data.get("quantity"),
            buy_exchange=trade_data.get("buy_exchange"),
            sell_exchange=trade_data.get("sell_exchange"),
            buy_price=trade_data.get("buy_price"),
            sell_price=trade_data.get("sell_price"),
            pnl=trade_data.get("pnl"),
            status=trade_data.get("status"),
            error=trade_data.get("error")
        )
        db.add(trade)
        db.commit()
    finally:
        db.close()

def save_balance(balance_data: dict):
    """Save balance snapshot to database"""
    db = SessionLocal()
    try:
        balance = Balance(
            exchange=balance_data.get("exchange"),
            asset=balance_data.get("asset"),
            available=balance_data.get("available"),
            locked=balance_data.get("locked"),
            total=balance_data.get("total")
        )
        db.add(balance)
        db.commit()
    finally:
        db.close()

def get_trades(limit: int = 20):
    """Retrieve recent trades"""
    db = SessionLocal()
    try:
        return db.query(Trade).order_by(Trade.timestamp.desc()).limit(limit).all()
    finally:
        db.close()

def get_daily_stats(date: str):
    """Get daily statistics"""
    db = SessionLocal()
    try:
        return db.query(DailyStats).filter(DailyStats.date == date).first()
    finally:
        db.close()
