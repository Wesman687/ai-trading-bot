

import traceback
from robot.trading_env import TradingEnv
from stable_baselines3 import PPO
from model.predictor import load_model_for_token, load_threshold_for_token,  load_feature_names_for_token
from config import models, RL_MODELS
from config import    HORIZONS,  WATCHED_PAIRS
from datetime import datetime, timezone
import os

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
        model = load_model_for_token(token, frame)
        feature_names = load_feature_names_for_token(token, frame)
        threshold = load_threshold_for_token(token, frame)

        models[token.upper()][frame] = {
            "model": model,
            "features": feature_names,
            "threshold": threshold,
        }

        msg = f"✅ Reloaded LLM model for {token.upper()} {frame} from model/latest/latest_model_{token.lower()}_{frame}.xgb"
        print(msg)
        log_reload_event(msg)

    except Exception as e:
        error_details = traceback.format_exc()
        msg = f"❌ Failed to reload {token.upper()} {frame}:\n{error_details}"
        print(msg)
        log_reload_event(msg)

def load_all_models():
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