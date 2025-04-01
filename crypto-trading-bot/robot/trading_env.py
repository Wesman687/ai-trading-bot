import os
import json
import random
import numpy as np
from pathlib import Path
from collections import deque
import logging
import gym
from gym import spaces
from data.utils.feature_data import sanitize_vector
import numpy as np
from datetime import datetime, timedelta

FEATURE_DIR = Path("data/daily/features")
WINDOW_SIZE = 20  # Number of timesteps for state
LOG_FILE = "logs/rl_trading.log"
os.makedirs("logs", exist_ok=True)
TRAILING_STOP_PCT = 0.01  # 1% trailing stop
TRAILING_CONFIDENCE_DECAY = 0.2     # Exit if confidence drops 20% from entry
CONFIDENCE_SMOOTHING_ALPHA = 0.8    # EWMA smoothing factor for confidence
MIN_HOLD_MINUTES = 3      


IMPORTANT_FEATURES = [
            "rsi", "macd_histogram", "volume_vs_median", "momentum_5",
            "macd_cross", "rsi_cross_50", "macd_persistence", "volume_surge",
            "trend_strength_5", "bearish_count_5", "bullish_count_5",
            "doji_count", "noise_ratio", "gap_pct", "macd_direction_3"
        ]


class TradingEnv(gym.Env):
    def __init__(self, token, max_steps=1000, use_confidence=True):
        self.use_confidence = use_confidence
        self.token = token.upper()
        self.file_path = FEATURE_DIR / f"{self.token}_features.jsonl"
        self.max_steps = max_steps

        # ✅ Setup per-token logging
        token_log_file = Path("logs") / f"rl_{self.token.lower()}.log"
        handler = logging.FileHandler(token_log_file)
        handler.setFormatter(logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        self.logger = logging.getLogger(f"RL_{self.token}")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(handler)
        self.logger.propagate = False  # Prevent double logging

        # Load data
        self.data = self.load_data()
        example_vector = self.get_feature_vector(self.data[0])

        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(WINDOW_SIZE * len(example_vector),),
            dtype=np.float32
        )

        self.reset()

        # Track stats
        self.total_reward = 0
        self.trades_taken = 0
        self.wins = 0
        self.losses = 0
        self.drawdowns = []

    def load_data(self):
        with open(self.file_path, "r") as f:
            lines = [json.loads(line) for line in f if line.strip()]
        return lines

    def reset(self):
        self.data = self.load_data()
        self.index = WINDOW_SIZE
        self.balance = 1000.0
        self.position = None
        self.total_reward = 0
        self.trades_taken = 0
        self.wins = 0
        self.losses = 0
        self.drawdowns = []

        self.history = deque(maxlen=WINDOW_SIZE)
        for i in range(WINDOW_SIZE):
            vec = self.get_feature_vector(self.data[i])
            if not np.all(np.isfinite(vec)):
                vec = np.nan_to_num(vec, nan=0.0, posinf=0.0, neginf=0.0)
            self.history.append(vec)

        return self._get_state()
    
    def _get_state(self):
        state = np.array(self.history).flatten()
        return sanitize_vector(state)

    

    def get_feature_vector(self, row):
        vec = [row.get(f, 0) for f in IMPORTANT_FEATURES]      
        return sanitize_vector(vec)
    
    def step_with_live_features(self, features_row):
        """
        Updates the internal state using new live features.
        Returns the updated observation state for external prediction.
        """
        self.history.append(self.get_feature_vector(features_row))
        return self._get_state()

      # 1% trailing stop

    def step(self, action):
        done = self.index >= len(self.data) - 1
        reward = 0
        if self.use_confidence:
            current_conf = row.get("confidence", 1.0)
            entry_conf = self.position.get("entry_confidence", 1.0)
            if current_conf < entry_conf * (1 - TRAILING_CONFIDENCE_DECAY):
                action = 3  # Exit due to confidence decay

        if self.index < len(self.data):
            vec = self.get_feature_vector(self.data[self.index])
            self.history.append(np.nan_to_num(vec, nan=0.0, posinf=0.0, neginf=0.0))

        row = self.data[self.index]
        price = row.get("close", 0)

        # --- Update peak/bottom price if in position ---
        if self.position:
            if self.position["direction"] == "long":
                self.position["peak_price"] = max(self.position.get("peak_price", price), price)
                peak = self.position["peak_price"]
                if price < peak * (1 - TRAILING_STOP_PCT):
                    action = 3  # Force exit
            elif self.position["direction"] == "short":
                self.position["bottom_price"] = min(self.position.get("bottom_price", price), price)
                bottom = self.position["bottom_price"]
                if price > bottom * (1 + TRAILING_STOP_PCT):
                    action = 3  # Force exit

        # --- Actions ---
        if action == 1 and self.position is None:
            self.position = {
                "entry_price": price,
                "direction": "long",
                "peak_price": price,
                "entry_confidence": row.get("confidence", 1.0),
                "smoothed_confidence": row.get("confidence", 1.0),
                "entry_time": row.get("timestamp") or datetime.now().isoformat()
            }
        elif action == 2 and self.position is None:
            self.position = {
                "entry_price": price,
                "direction": "short",
                "bottom_price": price,
                "entry_confidence": row.get("confidence", 1.0),
                "smoothed_confidence": row.get("confidence", 1.0),
                "entry_time": row.get("timestamp") or datetime.now().isoformat()
            }
            
        if self.use_confidence and self.position:
            current_conf = row.get("confidence", 1.0)
            prev_smooth = self.position.get("smoothed_confidence", current_conf)
            smoothed = (CONFIDENCE_SMOOTHING_ALPHA * prev_smooth) + ((1 - CONFIDENCE_SMOOTHING_ALPHA) * current_conf)
            self.position["smoothed_confidence"] = smoothed

            decay_trigger = self.position["entry_confidence"] * (1 - TRAILING_CONFIDENCE_DECAY)

            entry_time = datetime.fromisoformat(self.position["entry_time"])
            now = datetime.fromisoformat(row.get("timestamp")) if "timestamp" in row else datetime.now()
            hold_duration = (now - entry_time).total_seconds() / 60

            # Only allow confidence-based exit after min hold
            if hold_duration >= MIN_HOLD_MINUTES and smoothed < decay_trigger:
                action = 3  # trigger early exit due to confidence decay
        elif action == 3 and self.position is not None:
            # Close position
            entry = self.position["entry_price"]
            if self.position["direction"] == "long":
                reward = price - entry
            else:
                reward = entry - price

            self.balance += reward
            self.total_reward += reward
            self.trades_taken += 1
            if reward > 0:
                self.wins += 1
            else:
                self.losses += 1
            self.logger.info(
                f"[CLOSE] {self.token} | Action: {action} | Reward: {reward:.4f} | Balance: {self.balance:.2f}"
            )
            self.position = None

        self.index += 1
        if self.index < len(self.data):
            self.history.append(self.get_feature_vector(self.data[self.index]))

        if done:
            self.logger.info(
                f"[CLOSE] {self.token} | Action: {action} | Reward: {reward:.4f} | Balance: {self.balance:.2f} | "
                f"SmoothedConf: {smoothed:.3f} | EntryConf: {self.position.get('entry_confidence', 0):.3f}"
            )
            return self._get_state(), reward, done, {}

        return self._get_state(), reward, done, {}

    

# Example usage
if __name__ == "__main__":
    env = TradingEnv("BTC")
    state = env.reset()

    total_reward = 0
    for _ in range(200):
        action = random.choice([0, 1, 2, 3])
        next_state, reward, done, _ = env.step(action)
        total_reward += reward
        if done:
            break

    print(f"Total simulated reward: {total_reward:.2f}")
    logging.info(f"🎯 Final total reward after test run: {total_reward:.2f}")