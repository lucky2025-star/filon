"""
FastAPI app for the arbitrage bot dashboard and API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from core.price_monitor import PriceMonitor
from core.trade_executor import TradeExecutor
from core.inventory_manager import InventoryManager
from config.secrets import SecretsManager
from utils.logger import logger

app = FastAPI(title="Arbitrage Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount frontend static files
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

price_monitor = PriceMonitor()
trade_executor = TradeExecutor()
inventory_manager = InventoryManager()
secrets_manager = SecretsManager()

@app.get("/", response_class=HTMLResponse)
def root():
    """Serve dashboard"""
    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            return f.read()
    return "<h1>Dashboard not found</h1>"

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/validate-credentials")
def validate_credentials(credentials: dict):
    """Validate API credentials format before saving"""
    try:
        validation_results = {}
        
        for key, value in credentials.items():
            if not value or not value.strip():
                continue
            
            # Extract exchange name from key (e.g., "binance_api_key" -> "binance")
            parts = key.split("_")
            if len(parts) < 2:
                continue
            
            exchange_name = parts[0]
            credential_type = "_".join(parts[1:])
            
            # Check if we have both key and secret for this exchange
            api_key_key = f"{exchange_name}_api_key"
            api_secret_key = f"{exchange_name}_api_secret"
            
            api_key = credentials.get(api_key_key, "").strip()
            api_secret = credentials.get(api_secret_key, "").strip()
            
            # Skip if already validated for this exchange
            if exchange_name in validation_results:
                continue
            
            # Validation checks
            if not api_key or not api_secret:
                validation_results[exchange_name] = {
                    "valid": False,
                    "message": "❌ Both API Key and Secret are required"
                }
                continue
            
            # Check format - keys should have specific characteristics
            key_valid = True
            secret_valid = True
            issues = []
            
            # API Key validation
            if len(api_key) < 10:
                key_valid = False
                issues.append("API Key too short (min 10 chars)")
            if not api_key.replace("_", "").replace("-", "").isalnum():
                key_valid = False
                issues.append("API Key has invalid characters")
            
            # API Secret validation  
            if len(api_secret) < 10:
                secret_valid = False
                issues.append("Secret too short (min 10 chars)")
            if not api_secret.replace("_", "").replace("-", "").replace("+", "").replace("/", "").replace("=", "").isalnum():
                secret_valid = False
                issues.append("Secret has invalid characters")
            
            # Special validation for KuCoin (requires password)
            if exchange_name.lower() == "kucoin":
                kucoin_password = credentials.get(f"{exchange_name}_password", "").strip()
                if not kucoin_password:
                    validation_results[exchange_name] = {
                        "valid": False,
                        "message": "❌ KuCoin requires API Password/Passphrase"
                    }
                    continue
                if len(kucoin_password) < 4:
                    validation_results[exchange_name] = {
                        "valid": False,
                        "message": "❌ KuCoin password appears too short"
                    }
                    continue
            
            if not key_valid or not secret_valid:
                validation_results[exchange_name] = {
                    "valid": False,
                    "message": f"❌ Invalid format: {', '.join(issues)}"
                }
                continue
            
            # Basic format checks passed
            message = f"✅ {exchange_name.upper()} credentials format valid"
            if exchange_name.lower() == "kucoin":
                message = "✅ KuCoin (with password) format valid"
                
            validation_results[exchange_name] = {
                "valid": True,
                "message": message
            }
        
        return {
            "status": "success",
            "results": validation_results
        }
    except Exception as e:
        logger.error(f"Error validating credentials: {str(e)}")
        return {
            "status": "error",
            "message": f"Validation error: {str(e)}"
        }

@app.post("/save-credentials")
def save_credentials(credentials: dict):
    """Save and encrypt API credentials"""
    try:
        saved_count = 0
        for key, value in credentials.items():
            if value and value.strip():
                # Encrypt and save
                secrets_manager.save_secret(key, value)
                saved_count += 1
                logger.info(f"Credential saved: {key}")
        
        return {
            "status": "success",
            "message": f"Successfully saved and encrypted {saved_count} credentials",
            "count": saved_count
        }
    except Exception as e:
        logger.error(f"Error saving credentials: {str(e)}")
        return {
            "status": "error",
            "message": f"Error saving credentials: {str(e)}"
        }

@app.post("/delete-credentials")
def delete_credentials(data: dict):
    """Delete credentials for an exchange"""
    try:
        exchange = data.get("exchange", "").lower()
        
        if not exchange:
            return {
                "status": "error",
                "message": "Exchange name required"
            }
        
        # Delete all credentials for this exchange
        secrets = secrets_manager.load_secrets()
        keys_to_delete = [key for key in secrets.keys() if key.startswith(f"{exchange}_")]
        
        if not keys_to_delete:
            return {
                "status": "error",
                "message": f"No credentials found for {exchange}"
            }
        
        # Remove keys and save
        for key in keys_to_delete:
            del secrets[key]
        
        # Save updated secrets
        data_str = str(secrets).encode()
        encrypted = secrets_manager.fernet.encrypt(data_str)
        import os
        with open(secrets_manager.secrets_path, "wb") as f:
            f.write(encrypted)
        
        logger.info(f"Deleted {len(keys_to_delete)} credentials for {exchange}")
        
        return {
            "status": "success",
            "message": f"Deleted credentials for {exchange.upper()}",
            "deleted_count": len(keys_to_delete)
        }
    except Exception as e:
        logger.error(f"Error deleting credentials: {str(e)}")
        return {
            "status": "error",
            "message": f"Error deleting credentials: {str(e)}"
        }

@app.get("/check-credentials")
def check_credentials():
    """Check which credentials are stored and return masked versions"""
    try:
        secrets = secrets_manager.load_secrets()
        credential_status = {}
        
        # Map exchanges
        exchanges = ["binance", "kucoin", "mexc", "okx", "gateio", "bybit"]
        
        for exchange in exchanges:
            api_key_key = f"{exchange}_api_key"
            api_secret_key = f"{exchange}_api_secret"
            password_key = f"{exchange}_password"
            
            api_key = secrets.get(api_key_key, "")
            api_secret = secrets.get(api_secret_key, "")
            password = secrets.get(password_key, "")
            
            # Create masked versions for display (show first 4 and last 4 chars)
            if api_key:
                if len(api_key) > 8:
                    masked_key = api_key[:4] + "•" * (len(api_key) - 8) + api_key[-4:]
                else:
                    masked_key = "•" * len(api_key)
            else:
                masked_key = None
            
            if api_secret:
                if len(api_secret) > 8:
                    masked_secret = api_secret[:4] + "•" * (len(api_secret) - 8) + api_secret[-4:]
                else:
                    masked_secret = "•" * len(api_secret)
            else:
                masked_secret = None
            
            if password:
                if len(password) > 4:
                    masked_password = password[:2] + "•" * (len(password) - 4) + password[-2:]
                else:
                    masked_password = "•" * len(password)
            else:
                masked_password = None
            
            # Only include if at least api_key is present
            if api_key:
                credential_status[exchange] = {
                    "has_api_key": bool(api_key),
                    "has_api_secret": bool(api_secret),
                    "has_password": bool(password),
                    "api_key_masked": masked_key,
                    "api_secret_masked": masked_secret,
                    "password_masked": masked_password
                }
        
        return {
            "status": "success",
            "credentials": credential_status
        }
    except Exception as e:
        logger.error(f"Error checking credentials: {str(e)}")
        return {
            "status": "error",
            "message": f"Error checking credentials: {str(e)}",
            "credentials": {}
        }

@app.get("/prices")
def get_prices(pairs: str = "BTC/USDT,ETH/USDT"):
    """Get current prices for trading pairs
    
    Usage:
    - /prices?pairs=BTC/USDT,ETH/USDT
    - /prices (uses default BTC/USDT,ETH/USDT)
    """
    try:
        # Split the comma-separated pairs
        symbol_list = [p.strip() for p in pairs.split(",")]
        prices = price_monitor.fetch_prices(symbol_list)
        
        # Check which exchanges are configured
        configured_exchanges = list(price_monitor.exchange_manager.exchanges.keys())
        unconfigured = [ex for ex in ["binance", "kucoin", "mexc", "okx", "gateio", "bybit"] if ex not in configured_exchanges]
        
        return {
            "prices": prices,
            "configured_exchanges": configured_exchanges,
            "unconfigured_exchanges": unconfigured,
            "message": f"Prices from {len(configured_exchanges)} configured exchanges" if configured_exchanges else "⚠️ No exchanges configured - add API credentials in Settings"
        }
    except Exception as e:
        logger.error(f"Error fetching prices: {str(e)}")
        return {
            "prices": {},
            "error": str(e),
            "message": "Error fetching prices"
        }

@app.get("/prices/{symbols}")
def get_prices_legacy(symbols: str):
    """Legacy path-based prices endpoint for backward compatibility"""
    try:
        # Handle URL-encoded commas (%2C)
        symbols = symbols.replace("%2C", ",").replace("%2F", "/")
        symbol_list = [s.strip() for s in symbols.split(",")]
        prices = price_monitor.fetch_prices(symbol_list)
        
        # Check which exchanges are configured
        configured_exchanges = list(price_monitor.exchange_manager.exchanges.keys())
        
        return {
            "prices": prices,
            "configured_exchanges": configured_exchanges,
            "message": f"Prices from {len(configured_exchanges)} configured exchanges" if configured_exchanges else "⚠️ No exchanges configured"
        }
    except Exception as e:
        logger.error(f"Error fetching prices: {str(e)}")
        return {
            "prices": {},
            "error": str(e),
            "message": "Error fetching prices"
        }

@app.get("/opportunities")
def get_opportunities():
    """Get current arbitrage opportunities"""
    prices = price_monitor.get_cached_prices([])
    opportunities = price_monitor.detect_opportunities(prices)
    return opportunities

@app.get("/balances")
def get_balances():
    """Get balances across all exchanges"""
    balances = inventory_manager.get_all_balances()
    return balances

@app.get("/trades")
def get_trades(limit: int = 20):
    """Get trade history"""
    trades = trade_executor.get_trade_history(limit)
    return trades

@app.get("/status")
def get_bot_status():
    """Get bot status"""
    return {"message": "Bot is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
