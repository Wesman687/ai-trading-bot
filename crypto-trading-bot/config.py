# config.py



import os
from dotenv import load_dotenv


load_dotenv()

RL_MODELS = {}  # Store models per token

models = {}

BTCC_ACCESS_ID = os.getenv("BTCC_ACCESS_ID")
BTCC_SECRET_KEY = os.getenv("BTCC_SECRET_KEY")
BTCC_WS_BASE = os.getenv("BTCC_API_BASE", "wss://kapi1.btloginc.com:9082")

BTCC_SYMBOLS = {
    "BTCUSDT": 3355958,
    "XRPUSDT": 3750193,
    "SOLUSDT": 3750197
}
# Map tokens to Santiment slugs
SANTIMENT_SLUGS = {
    "BTC": "bitcoin",
    "XRP": "ripple",
    "SOL": "solana"
}

BUFFER_AMOUNT = 86400
DAYSBACK = 61

TOKENS = ["BTC", "XRP", "SOL"]
WATCHED_PAIRS = ["BTC/USDT", "XRP/USDT", "SOL/USDT"]

BINANCE_SYMBOLS = [pair.lower().replace("/", "") for pair in WATCHED_PAIRS]

MODEL_PATH = "model/latest_model.xgb"

MAX_CANDLES_PER_PAIR = 1440  # 24 hours of 1m candles

DAILY_DIR = "data/daily"
FEATURE_DIR = "data/daily/features"


CONFIDENCE_THRESHOLD = .8

TRADE_CONFIDENCE_THRESHOLD = 0.9
TRADE_CONFIG = {
    "trade_size": "compound",      # or use 100.0 for fixed
    "leverage": 1,
    "prediction_window": 5,  # how many minutes to hold the trade before evaluating
    "stop_loss_pct": 0.01,   # 1% SL
    "take_profit_pct": 0.02, # 2% TP
    "reverse_momentum_pct": 0.005
}

HORIZONS = {
    1: {
        "frame": "1m",
        "threshold": 0.0015
    },
    15: {
        "frame": "15m",
        "threshold": 0.003
    },
    60: {
        "frame": "1h",
        "threshold": 0.006
    },
    1440: {
        "frame": "1d",
        "threshold": 0.012
    }
}
HORIZON_WINDOWS  = {
    "1m": 5,       # minutes
    "15m": 15,
    "1h": 60,
    "1d": 240
}
MIN_TREND = {
    "1m": 0.3,   # was 0.4
    "15m": 0.25, # was 0.35
    "1h": 0.2,   # was 0.3
    "1d": 0.15   # was 0.25
}

STRATEGY_CONFIG = {
    "BTC": {
        "confidence_thresholds": {
            "1m": 0.75,
            "15m": 0.7,
            "1h": 0.68,
            "1d": 0.65
        },
        "confidence_override_threshold": 0.9
    },
    "XRP": {
        "confidence_thresholds": {
            "1m": 0.78,
            "15m": 0.74,
            "1h": 0.7,
            "1d": 0.66
        },
        "confidence_override_threshold": 0.9
    },
    "SOL": {
        "confidence_thresholds": {
            "1m": 0.77,
            "15m": 0.73,
            "1h": 0.7,
            "1d": 0.66
        },
        "confidence_override_threshold": 0.9
    }
}



HIGHER_TFS = ["1h", "4h", "1d"]


WEIGHTS = {
    "5min": 1.0,
    "15min": 0.7,
    "1h": 0.5,
    "4h": 0.3,
    "1d": 0.1
}


TIMEFRAMES = {
    "15m": {"rule": "15min", "weight": 0.4},
    "1h": {"rule": "1h", "weight": 0.3},
    "4h": {"rule": "4h", "weight": 0.2},
    "1d": {"rule": "1d", "weight": 0.1},
}
