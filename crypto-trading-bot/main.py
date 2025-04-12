
import threading
from data.ws_client import init_all_buffers, start_ws_listener
from features.feature_aggregator import aggregate_features
from config import    HORIZONS,  WATCHED_PAIRS
from data.daily_fetcher import fetch_all_candles
from trading.momentum import add_live_momentum_features
import asyncio
from model.predictor import log_prediction_batch, predict
import platform
import json
from config import models, RL_MODELS
from robot.helper_function import evaluate_rl_bot
from data.utils.convert_to_features import convert_all_from_daily
from model.utils.model_watcher import start_model_reload_watcher
from utils.model_loaders import load_all_models


booting_up = True  # global flag to suppress reloads if needed

async def boot():
    # Async boot step
    await fetch_all_candles()

    # Sync steps after async completes
    convert_all_from_daily(days=3)   # CSV -> feature JSONL
    load_all_models()                # Load XGB, RL, etc.

    global booting_up
    booting_up = False               # ✅ Now it's safe to start watching

    # Start model file watcher
    threading.Thread(target=start_model_reload_watcher, daemon=True).start()

    # Start main async app loop
    await main()   


        
def symbol_from_pair(pair: str) -> str:
    return pair.replace("/USDT", "").upper()

def validate_features(expected_features, features):
    """Validate if all expected features are present in the features dictionary."""
    missing_features = []
    for feature in expected_features:
        if feature not in features:
            missing_features.append(feature)

    if missing_features:
        print(f"⚠️ Missing features: {missing_features}")
        


async def main():
    print("Checking Historical Data and Downloading if needed...")

    

    await init_all_buffers()
    print("Bootstrapping historical data...")
    current_prices = {}
    
    async def on_price_update(pair, latest_data, latest_feature, candle_history, symbol, feature_buffer):
        token = pair.split("/")[0]        
        
        # RL agent (per token)
        result = evaluate_rl_bot(token, latest_feature, RL_MODELS)
        if result:
            print(f"[RL] {token} | Action: {result['action']} | Reward: {result['reward']:.4f}")
                
        current_prices[pair] = latest_data["close"]
        predictions = {}
        features_by_horizon = {}
        for _, info in HORIZONS.items():
            frame = info["frame"]
            threshold = info["threshold"]

            model = models[token][frame]["model"]
            feature_names = models[token][frame]["features"]

            features = aggregate_features(
                pair,
                feature_buffer[symbol],
                latest_feature,
                feature_names,
                candle_history[symbol]
            )
            validate_features(feature_names, features)
            features.update(add_live_momentum_features(feature_buffer[symbol]))

            predictions[frame] = predict(model, features, feature_names, threshold, token, frame)
            features_by_horizon[frame] = features
            from utils.send_trader import send_signal_to_trading_server
            
            debug_path = f"logs/feature_debug_{pair}_{frame}.txt"
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(f"🔎 Feature Snapshot for {pair} {frame} \n")
                f.write("=" * 40 + "\n")
                for key in sorted(features.keys()):
                    val = features[key]
                    try:
                        if isinstance(val, float):
                            f.write(f"{key:<30}: {val:.6f}\n")
                        else:
                            f.write(f"{key:<30}: {val}\n")
                    except Exception as e:
                        f.write(f"{key:<30}: ❌ Error printing value ({e})\n")
                        
        prediction_entries = [
            (
                predictions[frame]["probability"],
                predictions[frame]["threshold"],
                predictions[frame]["direction"],
                frame
            )
            for frame in predictions
        ]

        # Get latest price from incoming data
        latest_price = latest_data["close"]

        # Log predictions for all frames
        log_prediction_batch(token, latest_price, prediction_entries)
        try:
            await send_signal_to_trading_server(token, latest_data, features_by_horizon, predictions, result)
        except Exception as e:
            print(f"❌ Error sending signal to trading server: {e}")
    
    print("Starting WebSocket listeners...")
    await start_ws_listener([s.lower().replace("/", "") for s in WATCHED_PAIRS], on_price_update)


if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(boot())