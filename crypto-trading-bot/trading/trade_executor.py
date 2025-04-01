# trading/trade_executor.py
from datetime import datetime, timezone
import time
from .btcc_auth import generate_signature
from trading.paper_wallet import simulate_trade

import requests

# In-memory record of trades
TRADE_LOG = []

def execute_trade(pair: str, decision: dict):
    """
    Simulates or executes a trade based on the selected signal decision.
    This version supports trade duration and richer metadata.
    """
    direction = decision["direction"]
    confidence = decision["confidence"]
    horizon = decision["horizon"]
    duration = decision["duration"]
    features = decision["features"]
    price = decision.get("price") or features.get("close")
    timestamp = datetime.now(timezone.utc).isoformat()
    multiplier = decision.get("multiplier", 1.0)

    log_entry = {
        "timestamp": timestamp,
        "pair": pair,
        "direction": direction,
        "confidence": round(confidence, 5),
        "horizon": horizon,
        "duration": duration,
        "entry_price": price,
        "features": {k: features[k] for k in features if isinstance(features[k], (int, float))},
        "multiplier": multiplier,
    }

    # Add to internal log or persist to file/db
    TRADE_LOG.append(log_entry)

    print(f"[TRADE] {timestamp} | {pair} | {direction.upper()} | Horizon: {horizon} | Hold: {duration}m | Confidence: {confidence:.3f}, multiplier: {multiplier:.2f} | Price: {price:.2f}")
    
    # Optionally simulate actual trade logic
    simulate_trade(
        pair=pair,
        direction=direction,
        confidence=confidence,
        price=price,
        features=features,
        duration_minutes=duration,
        multiplier=multiplier,
    )
  
  
  
    
def place_btcc_market_order(token, access_id, secret_key, amount):
    tm = int(time.time())
    params = {
        "access_id": access_id,
        "tm": tm,
        "market": token,        # e.g. BTCUSDT
        "side": 1,              # 1 = Buy, 2 = Sell
        "amount": str(amount),  # Needs to be string
        "option": 0,            # Default = GTC
        "source": "cryptobot"
    }

    signature = generate_signature(params, secret_key)
    headers = { "authorization": signature }
    response = requests.post(
        "http://spot_api.cryptouat.com:9910/btcc_api_trade/order/market",
        headers=headers,
        json=params
    )
    print(response.json())
