# Crypto Cross-Exchange Arbitrage Bot

A professional-grade Python bot for detecting and executing arbitrage trades across 6 major cryptocurrency exchanges.

## Features

✅ **Multi-Exchange Support**: Binance, KuCoin, MEXC, OKX, Gate.io, Bybit
✅ **Real-Time Price Monitoring**: WebSocket and REST API integration via CCXT
✅ **Spread Detection Algorithm**: Calculates net profits after fees
✅ **Automated Trading**: Executes buy/sell orders based on configurable thresholds
✅ **Risk Management**: Circuit breakers, daily loss limits, exposure tracking
✅ **Inventory Management**: Tracks balances, detects drift, suggests rebalancing
✅ **Trade History**: Persists trades to SQLite database
✅ **Web Dashboard**: Real-time monitoring interface with statistics
✅ **Telegram Alerts**: Notifications for profitable opportunities and errors
✅ **Secure Credential Storage**: Encrypted API keys using Fernet

## Project Structure

```
crypto_arbitrage_bot/
├── config/
│   ├── config.py           # Settings and configuration
│   ├── settings.py         # User preferences
│   └── secrets.py          # Encrypted credential storage
├── exchanges/
│   ├── exchange_manager.py # CCXT unified interface
│   ├── ccxt_wrapper.py     # Exchange wrapper
│   └── websocket_feeder.py # Real-time price feeds
├── core/
│   ├── arbitrage_engine.py # Profit calculations
│   ├── price_monitor.py    # Price monitoring
│   ├── trade_executor.py   # Order execution
│   ├── inventory_manager.py# Balance tracking
│   └── risk_manager.py     # Risk controls
├── database/
│   ├── db.py               # Database operations
│   ├── models.py           # SQLAlchemy models
│   └── migrations/
├── api/
│   ├── app.py              # FastAPI application
│   ├── routes.py           # API endpoints
│   └── websocket_handler.py# WebSocket handlers
├── frontend/
│   ├── index.html          # Dashboard UI
│   ├── dashboard.js        # Frontend logic
│   └── styles.css          # Dashboard styling
├── utils/
│   ├── logger.py           # Logging utility
│   ├── notifications.py    # Telegram notifications
│   └── helpers.py          # Helper functions
├── tests/
│   ├── test_arbitrage_engine.py
│   ├── test_exchange_manager.py
│   └── test_trade_executor.py
├── main.py                 # Bot entry point
└── requirements.txt        # Dependencies
```

## Installation

1. Clone the repository:
```bash
git clone <repo_url>
cd crypto_arbitrage_bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up configuration:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Initialize the database:
```bash
python -c "from database.db import init_db; init_db()"
```

## Configuration

### Environment Variables

Create a `.env` file with your API credentials:

```env
DEBUG=False
EXCHANGES=binance,kucoin,mexc,okx,gateio,bybit

# Exchange API Keys
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret

KUCOIN_API_KEY=your_key
KUCOIN_API_SECRET=your_secret

# ... repeat for other exchanges

# Telegram
TELEGRAM_API_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id

# Bot Settings
MIN_SPREAD_THRESHOLD=0.3
MAX_POSITION_SIZE=1.0
MAX_CONCURRENT_TRADES=3
DAILY_LOSS_LIMIT=-100.0
MAX_TOTAL_EXPOSURE=10.0
```

### Secure API Key Storage

API keys are encrypted using Fernet symmetric encryption:

```python
from config.secrets import SecretsManager

secrets = SecretsManager()
# Save credentials (run once)
secrets.save_secret("binance_api_key", "your_key")
secrets.save_secret("binance_api_secret", "your_secret")

# Retrieve credentials
api_key = secrets.get_secret("binance_api_key")
```

## Usage

### Start the Bot

```bash
python main.py
```

The bot will:
1. Connect to all configured exchanges
2. Start monitoring prices
3. Detect arbitrage opportunities
4. Execute trades if auto-trading is enabled

### Run the Dashboard

```bash
python -m uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

Then open `http://localhost:8000` in your browser.

## Core Modules

### Price Monitor
- Fetches OHLCV data from all exchanges
- Maintains local price cache
- Detects arbitrage opportunities
- Calculates spreads accounting for fees

```python
from core.price_monitor import PriceMonitor

monitor = PriceMonitor()
prices = monitor.fetch_prices(["BTC/USDT", "ETH/USDT"])
opportunities = monitor.detect_opportunities(prices, min_spread=0.3)
```

### Arbitrage Engine
- Calculates profit for trades
- Ranks opportunities by profitability
- Validates trades against available funds

```python
from core.arbitrage_engine import ArbitrageEngine

engine = ArbitrageEngine(min_spread=0.3)
profit = engine.calculate_profit(
    buy_price=45000,
    sell_price=45225,
    quantity=0.1,
    buy_fee=0.001,
    sell_fee=0.001
)
```

### Trade Executor
- Executes buy/sell orders
- Tracks order status
- Maintains trade history
- Calculates P&L

```python
from core.trade_executor import TradeExecutor

executor = TradeExecutor()
result = executor.execute_arbitrage_trade(
    buy_exchange="binance",
    sell_exchange="kucoin",
    symbol="BTC/USDT",
    quantity=0.1
)
```

### Inventory Manager
- Tracks balances across exchanges
- Detects inventory drift
- Suggests rebalancing trades
- Calculates portfolio value

```python
from core.inventory_manager import InventoryManager

inventory = InventoryManager()
balances = inventory.get_all_balances()
drift = inventory.calculate_drift(balances, "BTC")
```

### Risk Manager
- Tracks daily P&L
- Enforces exposure limits
- Circuit breaker logic
- Risk status monitoring

```python
from core.risk_manager import RiskManager

risk = RiskManager(daily_loss_limit=-100, max_exposure=10)
risk.record_trade({"pnl": 50, "status": "completed"})
can_trade = risk.can_trade()
```

## API Endpoints

- `GET /health` - Health check
- `GET /prices/{symbols}` - Get current prices
- `GET /opportunities` - Get arbitrage opportunities
- `GET /balances` - Get account balances
- `GET /trades` - Get trade history
- `GET /status` - Get bot status

## Telegram Notifications

```python
from utils.notifications import TelegramNotifier

notifier = TelegramNotifier()
notifier.send_message(chat_id="1395251148", text="✅ Profitable trade detected!")
```

## Database

Trades, balances, and statistics are persisted to SQLite:

- `trades` - Individual trade records
- `balances` - Balance snapshots
- `daily_stats` - Daily aggregated statistics

## Alerts & Logging

- Console and file logging to `logs/`
- Telegram alerts for:
  - Profitable opportunities
  - Trade execution
  - Errors and failures
  - Risk threshold breaches

## Testing

```bash
python -m pytest tests/
```

## Key Algorithms

### Spread Detection
```
spread % = ((sell_price - buy_price) / buy_price) * 100 - buy_fee% - sell_fee%
```

### Profit Calculation
```
profit = (sell_price * qty - sell_fee) - (buy_price * qty + buy_fee)
```

### Inventory Drift
```
drift % = ((actual - ideal) / ideal) * 100
```

## Performance Tips

1. **Rate Limits**: CCXT automatically handles exchange rate limits
2. **Caching**: Prices are cached locally to reduce API calls
3. **Async Operations**: Use asyncio for non-blocking I/O
4. **Database Indexing**: Queries are optimized with proper indexes

## Risk Management

- Daily loss limits prevent catastrophic losses
- Circuit breaker pauses trading on errors
- Max exposure prevents over-leverage
- Position sizing based on available funds
- Manual trade approval available

## Security

- API keys encrypted with Fernet
- Never log sensitive credentials
- Environment variables for secrets
- Database credentials in `.env`
- CORS enabled for dashboard

## Troubleshooting

**Connection Issues**
- Verify API keys are correct
- Check exchange status pages
- Ensure rate limits aren't exceeded

**No Opportunities**
- Increase monitoring pairs
- Lower min spread threshold
- Check exchange connectivity

**Trades Not Executing**
- Verify sufficient balance
- Check order size limits
- Review risk manager status

## Future Enhancements

- [ ] WebSocket real-time feeds
- [ ] Machine learning opportunity prediction
- [ ] Advanced portfolio optimization
- [ ] Futures hedging strategies
- [ ] Mobile app support
- [ ] Advanced backtesting engine

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Support

For issues, questions, or suggestions, please open an issue on GitHub or contact the team.

---

**Disclaimer**: Cryptocurrency trading is risky. Use this bot at your own risk. Test thoroughly on testnet before using with real funds.
