"""
Database models for storing bot data.
"""
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Trade(Base):
    """Trade record model"""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True)
    trade_id = Column(String, unique=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    symbol = Column(String)
    quantity = Column(Float)
    buy_exchange = Column(String)
    sell_exchange = Column(String)
    buy_price = Column(Float)
    sell_price = Column(Float)
    pnl = Column(Float)
    status = Column(String)
    error = Column(String, nullable=True)

class Balance(Base):
    """Balance snapshot model"""
    __tablename__ = "balances"
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    exchange = Column(String)
    asset = Column(String)
    available = Column(Float)
    locked = Column(Float)
    total = Column(Float)

class DailyStats(Base):
    """Daily statistics model"""
    __tablename__ = "daily_stats"
    
    id = Column(Integer, primary_key=True)
    date = Column(String)
    total_trades = Column(Integer)
    winning_trades = Column(Integer)
    losing_trades = Column(Integer)
    total_pnl = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
