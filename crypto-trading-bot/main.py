
from pathlib import Path
import threading
import aiohttp
import joblib
from data.ws_client import init_all_buffers, start_ws_listener
from features.feature_aggregator import aggregate_features
from model.predictor import load_model_for_token, load_threshold_for_token, predict, load_feature_names_for_token
from trading.strategy import evaluate_multi_signal
from trading.trade_executor import execute_trade
from trading.paper_wallet import  export_account_snapshot, export_open_trades, log_live_account_status, log_live_snapshot, simulate_trade, update_trade_outcomes
from config import    HORIZONS,  WATCHED_PAIRS
from data.daily_fetcher import fetch_all_candles
from trading.momentum import add_live_momentum_features
import asyncio
from datetime import datetime, timedelta, timezone
import os
import platform
import json
from model.predictor import load_feature_names_for_token
from stable_baselines3 import PPO
from robot.trading_env import TradingEnv  # or wherever it's located
from robot.helper_function import evaluate_rl_bot
import xgboost as xgb
RL_MODELS = {}  # Store models per token

models = {}
async def retrain_daily():
    while True:
        now = datetime.now(timezone.utc)
        if now.hour == 1 and now.minute == 0:
            print("⏳ [Retrain] Starting daily retraining...")

            for pair in WATCHED_PAIRS:
                token = pair.split("/")[0].upper()

                # ✅ Step 1: Refresh 7-day split data
                print(f"🔄 [Retrain] Refreshing 7-day history for {token}")

                # ✅ Step 2: Aggregate all 7d CSVs into a training file
                daily_dir = "data/daily"
                csv_out = f"data/logs/{token}USDT_ohlcv.csv"
                with open(csv_out, "w") as outfile:
                    header_written = False
                    for filename in sorted(os.listdir(daily_dir)):
                        if filename.startswith(f"{token}USDT_1m") and filename.endswith(".csv"):
                            with open(os.path.join(daily_dir, filename), "r") as infile:
                                lines = infile.readlines()
                                if not header_written:
                                    outfile.write(lines[0])  # write header once
                                    header_written = True
                                outfile.writelines(lines[1:])  # skip header after first
                    

                # ✅ Step 3: Run training
                cmd = f"python model/train_local.py --csv {csv_out} --token {token}"
                print(f"📦 [Retrain] Running: {cmd}")
                exit_code = os.system(cmd)

                if exit_code == 0:
                    print(f"✅ [Retrain] {token} training completed.")
                else:
                    print(f"❌ [Retrain] {token} failed with exit code {exit_code}")

            await asyncio.sleep(60)  # wait 1 minute so it doesn’t double run
        else:
            await asyncio.sleep(30)

async def test_binance_connection():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.binance.com/api/v3/time") as resp:
                if resp.status == 200:
                    print("✅ Binance API is reachable")
                else:
                    print(f"⚠️ Binance API returned status {resp.status}")
    except Exception as e:
        print(f"❌ Could not reach Binance API: {e}")
        
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
        
        
LOG_FILE = "logs/model_reload.log"
os.makedirs("logs", exist_ok=True)

def log_reload_event(message: str):
    timestamp = datetime.now(timezone.utc).isoformat()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def reload_rl_model(token):
    model_path = f"models/ppo_trading_agent/{token}/ppo_trading_{token}.zip"
    env = TradingEnv(token)
    RL_MODELS[token] = {
        "env": env,
        "model": PPO.load(model_path, env=env, device="cpu")
    }
    log_reload_event(f"✅ RL model reloaded for {token} from {model_path}")
        
def reload_llm_model(token, frame):
    try:
        loaded = load_model_for_token(token, frame)
        feature_names = loaded["features"]
        threshold = loaded["threshold"]
        model = loaded["model"]

        models[token.upper()][frame] = {
            "model": model,
            "features": feature_names,
            "threshold": threshold,
        }

        msg = f"✅ Reloaded LLM model for {token.upper()} {frame} from model/latest/latest_model_{token.lower()}_{frame}.xgb"
        print(msg)
        log_reload_event(msg)

    except Exception as e:
        msg = f"❌ Failed to reload {token.upper()} {frame}: {e}"
        print(msg)
        log_reload_event(msg)


async def main():
    print("Checking Historical Data and Downloading if needed...")
    await fetch_all_candles()
    from data.utils.convert_to_features import convert_all_from_daily
    convert_all_from_daily(days=3)
    
    for pair in WATCHED_PAIRS:
        token = pair.split("/")[0].upper()
        model_filename = f"ppo_trading_{token}.zip"
        model_path = os.path.join("models", "ppo_trading_agent", token, model_filename)

        try:
            env = TradingEnv(token)
            model = PPO.load(model_path, env=env, device="cpu") 
            RL_MODELS[token] = {
                "env": env,
                "model": model
            }
            print(f"✅ Loaded RL model for {token}")
        except Exception as e:
            print(f"❌ Failed to load model for {token}: {e}")
    for pair in WATCHED_PAIRS:
        token = pair.split("/")[0]
        models[token] = {}

        for _, info in HORIZONS.items():
            try:
                frame = info["frame"]
                threshold = info["threshold"]
                
                models[token][frame] = {
                    "model": load_model_for_token(token, frame),
                    "features": load_feature_names_for_token(token, frame),
                    "threshold": threshold,
                }
            except Exception as e:
                print(f"❌ Failed to load {token.upper()} model for {info}: {e}")
    await init_all_buffers()
    print("Bootstrapping historical data...")
    current_prices = {}
    
    async def on_price_update(pair, latest_data, latest_feature, candle_history, symbol, feature_buffer):
        token = pair.split("/")[0]
        
        
        with open(f"logs/price_history/{pair.replace('/', '_')}.jsonl", "a") as f:
            f.write(json.dumps(latest_data, default=str) + "\n")
        
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

            predictions[frame] = predict(model, features, feature_names, threshold, token)
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

        await send_signal_to_trading_server(token, latest_data, features_by_horizon, predictions, result)

    
    print("Starting WebSocket listeners...")
    await start_ws_listener([s.lower().replace("/", "") for s in WATCHED_PAIRS], on_price_update)

if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    from model.utils.model_watcher import start_model_reload_watcher
    threading.Thread(target=start_model_reload_watcher, daemon=True).start()
    asyncio.run(main())
    
