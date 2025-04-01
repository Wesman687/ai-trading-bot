import json
import os

TOKENS = ["sol", "btc", "eth"]  # Add more if needed

# Correct feature list — make sure this matches your full model input
FEATURES = [
    "open", "high", "low", "close", "volume", "sma_20", "ema_20", "rsi", "macd", "macd_signal", "bb_upper", "bb_lower",
    "open_1h", "high_1h", "low_1h", "close_1h", "volume_1h", "sma_20_1h", "ema_20_1h", "rsi_1h", "macd_1h", "macd_signal_1h", "bb_upper_1h", "bb_lower_1h",
    "open_4h", "high_4h", "low_4h", "close_4h", "volume_4h", "sma_20_4h", "ema_20_4h", "rsi_4h", "macd_4h", "macd_signal_4h", "bb_upper_4h", "bb_lower_4h",
    "open_1d", "high_1d", "low_1d", "close_1d", "volume_1d", "sma_20_1d", "ema_20_1d", "rsi_1d", "macd_1d", "macd_signal_1d", "bb_upper_1d", "bb_lower_1d"
]

for token in TOKENS:
    path = f"model/{token.lower()}_features_selected.json"
    os.makedirs("model", exist_ok=True)
    with open(path, "w") as f:
        json.dump(FEATURES, f, indent=2)
    print(f"✅ Saved features for {token.upper()} → {path}")
