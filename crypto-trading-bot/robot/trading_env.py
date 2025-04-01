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
from .helper_function import update_trailing_logic, apply_confidence_decay, compute_extended_reward, shape_reward_with_duration

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

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
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
            self.history.append(np.nan_to_num(vec, nan=0.0, posinf=0.0, neginf=0.0))

        observation = self._get_state()
        info = {}
        return observation, info
    
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
        exit_reason = "manual_close"  # For extended logging (optional)

        if self.index < len(self.data):
            vec = self.get_feature_vector(self.data[self.index])
            self.history.append(np.nan_to_num(vec, nan=0.0, posinf=0.0, neginf=0.0))

        row = self.data[self.index]
        price = row.get("close", 0)

        # --- Update peak/bottom price if in position ---
        if self.position and update_trailing_logic(self.position, row, stop_pct=TRAILING_STOP_PCT):
            action = 3
            exit_reason = "trailing_stop"

        # --- Actions ---
        if action == 1 and self.position is None:
            self.position = {
                "entry_price": price,
                "direction": "long",
                "peak_price": price,
                "entry_confidence": row.get("confidence", 1.0),
                "smoothed_confidence": row.get("confidence", 1.0),
                "entry_time": row.get("timestamp") or datetime.now().isoformat(),
                "duration_minutes": 5
            }
        elif action == 2 and self.position is None:
            self.position = {
                "entry_price": price,
                "direction": "short",
                "peak_price": price,
                "entry_confidence": row.get("confidence", 1.0),
                "smoothed_confidence": row.get("confidence", 1.0),
                "entry_time": row.get("timestamp") or datetime.now().isoformat(),
                "duration_minutes": 5
            }

        if self.use_confidence and self.position and apply_confidence_decay(
            self.position,
            row,
            decay_threshold=TRAILING_CONFIDENCE_DECAY,
            min_hold_minutes=MIN_HOLD_MINUTES,
            alpha=CONFIDENCE_SMOOTHING_ALPHA
        ):
            action = 3
            exit_reason = "confidence_decay"

        if action == 3 and self.position is not None:
            # --- Calculate reward before dropping position ---
            entry = self.position["entry_price"]
            entry_conf = self.position.get("entry_confidence", 0)

            if self.position["direction"] == "long":
                reward = price - entry
            else:
                reward = entry - price

            reward += compute_extended_reward(self.token, self.position, row, reward)
            reward = shape_reward_with_duration(self.position, row, reward)
            self.balance += reward
            self.total_reward += reward
            self.trades_taken += 1
            if reward > 0:
                self.wins += 1
            else:
                self.losses += 1
                self.drawdowns.append(abs(reward))

            self.logger.info(
                f"[CLOSE] {self.token} | Action: {action} | Reward: {reward:.4f} | Balance: {self.balance:.2f} | "
                f"EntryConf: {entry_conf:.3f} | Reason: {exit_reason or 'manual'}"
            )
            self.position = None

        self.index += 1
        if self.index < len(self.data):
            self.history.append(self.get_feature_vector(self.data[self.index]))

        terminated = done  # natural end of episode
        truncated = False  # or True if you implement a step/time limit manually

        if done:
            self.logger.info(
                f"[CLOSE] {self.token} | Action: {action} | Reward: {reward:.4f} | Balance: {self.balance:.2f} | "
                f"Reason: {exit_reason}"
            )
            return self._get_state(), reward, terminated, truncated, {}

        return self._get_state(), reward, False, False, {}


    

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