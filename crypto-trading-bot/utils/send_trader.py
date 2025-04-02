

import aiohttp
import numpy as np
import pandas as pd
from datetime import datetime

def serialize_payload(obj):
    if isinstance(obj, dict):
        return {k: serialize_payload(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_payload(v) for v in obj]
    elif isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    elif isinstance(obj, (np.integer, int)):
        return int(obj)
    elif isinstance(obj, (np.floating, float)):
        return float(round(obj, 6))  # Round floats for cleaner JSON
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.to_dict()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict(orient="records")
    else:
        return obj
    
async def send_signal_to_trading_server(token, candle, features_by_horizon, predictions, rl_response=None):
    signal_payload = {
        "token": token,
        "candle": candle,
        "features": features_by_horizon,
        "predictions": predictions,
        "rl_response": rl_response,
    }

    serialized_payload = serialize_payload(signal_payload)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("http://localhost:5000/signal/update", json=serialized_payload) as resp:
                if resp.status != 200:
                    print(f"❌ Failed to send signal: {await resp.text()}")
                else:
                    print(f"📤 Sent signal for {token} → Trading Server")
    except Exception as e:
        print(f"⚠️ Could not connect to trading server: {e}")