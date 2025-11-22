import ccxt

# Paste your NEW keys here (only on your local machine)
api_key = "SIWs01gSmfcYXKWSD6bxIgAZPRPgrynq1pQBU8u2OtiBZX78IDubGtzPhs10wH0C"
api_secret = "gohO8DopC1P02uRbCZy6Nl92OMUiz7PHmUqAdaF9WGN0k9zlz0rO9eufkdyJcvTq"

binance = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
})

try:
    print("[1/3] Fetching balance...")
    balance = binance.fetch_balance()
    print("✅ Balance fetch SUCCESS!")
    
    # Show balances
    has_balance = False
    for asset, amounts in balance.items():
        if amounts['total'] > 0 and asset not in ['free', 'used', 'info']:
            print(f"   {asset}: {amounts['total']}")
            has_balance = True
    
    if not has_balance:
        print("   (No balances - account is empty)")
    
    print("\n[2/3] Fetching ticker...")
    ticker = binance.fetch_ticker('BTC/USDT')
    print(f"✅ Ticker fetch SUCCESS!")
    print(f"   BTC/USDT - Bid: {ticker['bid']}, Ask: {ticker['ask']}")
    
    print("\n[3/3] Fetching account info...")
    account = binance.fetch_account()
    print(f"✅ Account info SUCCESS!")
    print(f"   Account type: {account.get('type', 'unknown')}")
    
    print("\n" + "="*50)
    print("✅✅✅ ALL TESTS PASSED - API WORKING! ✅✅✅")
    print("="*50)
    
except Exception as e:
    print(f"❌ Error: {e}")