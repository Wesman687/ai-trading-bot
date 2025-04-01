

import pandas as pd


def add_live_momentum_features(history):
    df = pd.DataFrame(history[-5:])  # use last 5 candles for recent activity

    if len(df) < 2:
        return {}

    return {
        "volatility_5": df["high"].max() - df["low"].min(),
        "momentum_5": df["close"].iloc[-1] - df["close"].iloc[0],
        "candle_spread": df["high"].iloc[-1] - df["low"].iloc[-1],
        "candle_body": abs(df["close"].iloc[-1] - df["open"].iloc[-1]),
        "volume_surge": df["volume"].iloc[-1] / (df["volume"].mean() + 1e-6),
        
    }