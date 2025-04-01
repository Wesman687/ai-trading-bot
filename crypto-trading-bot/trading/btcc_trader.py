# btcc_trader.py
import time
import requests
import os
from dotenv import load_dotenv
from btcc_auth import generate_signature

load_dotenv()

# Config
BTCC_API_BASE = os.getenv("BTCC_API_BASE", "https://api.btcc.com")
ACCESS_ID = os.getenv("BTCC_ACCESS_ID")
SECRET_KEY = os.getenv("BTCC_SECRET_KEY")
REAL_TRADING_ENABLED = os.getenv("REAL_TRADING_ENABLED", "false").lower() == "true"

# --- Place Market Order ---
def place_market_order(pair: str, side: str, amount: float):
    if not REAL_TRADING_ENABLED:
        print(f"[DRY RUN] Would place {side.upper()} {amount} of {pair}")
        return {"status": "dry_run"}

    tm = int(time.time())
    side_code = 1 if side.lower() == "buy" else 2

    params = {
        "access_id": ACCESS_ID,
        "tm": tm,
        "market": pair.upper(),  # e.g. BTCUSDT
        "side": side_code,
        "amount": str(amount),
        "option": 0,
        "source": "cryptobot"
    }

    signature = generate_signature(params, SECRET_KEY)
    headers = {"authorization": signature}

    try:
        res = requests.post(f"{BTCC_API_BASE}/btcc_api_trade/order/market", headers=headers, json=params)
        data = res.json()
        print(f"✅ Order Response: {data}")
        return data
    except Exception as e:
        print(f"❌ Order Failed: {e}")
        return {"status": "error", "error": str(e)}

# --- Get Account Balance ---
def get_balance():
    tm = int(time.time())
    params = {
        "access_id": ACCESS_ID,
        "tm": tm,
    }
    signature = generate_signature(params, SECRET_KEY)
    headers = {"authorization": signature}

    try:
        res = requests.get(f"{BTCC_API_BASE}/btcc_api_trade/fund/list", headers=headers, params=params)
        data = res.json()
        print("💰 Balance:", data)
        return data
    except Exception as e:
        print(f"❌ Balance Fetch Failed: {e}")
        return {"status": "error", "error": str(e)}