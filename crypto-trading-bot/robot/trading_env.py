import os
import json
import numpy as np
from pathlib import Path
from collections import deque
import logging
import gym
from gym import spaces
from datetime import datetime, timedelta
from data.utils.feature_data import sanitize_vector
from .helper_function import (
    update_trailing_logic,
    apply_confidence_decay,
    compute_extended_reward,
    shape_reward_with_duration,
    small_positional_bonus,
)

FEATURE_DIR = Path("data/daily/features")
WINDOW_SIZE = 20
LOG_FILE = "logs/rl_trading.log"
os.makedirs("logs", exist_ok=True)

TRAILING_STOP_PCT = 0.01
TRAILING_CONFIDENCE_DECAY = 0.2
CONFIDENCE_SMOOTHING_ALPHA = 0.8
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

        token_log_file = Path("logs") / f"rl_{self.token.lower()}.log"
        handler = logging.FileHandler(token_log_file)
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"))

        self.logger = logging.getLogger(f"RL_{self.token}")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(handler)
        self.logger.propagate = False

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
        self.total_reward = 0
        self.trades_taken = 0
        self.wins = 0
        self.losses = 0
        self.drawdowns = []

    def load_data(self):
        with open(self.file_path, "r") as f:
            return [json.loads(line) for line in f if line.strip()]

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

        return self._get_state(), {}

    def _get_state(self):
        return sanitize_vector(np.array(self.history).flatten())

    def get_feature_vector(self, row):
        return sanitize_vector([row.get(f, 0) for f in IMPORTANT_FEATURES])

    def step_with_live_features(self, features_row):
        self.history.append(self.get_feature_vector(features_row))
        return self._get_state()

    def step(self, action):
        done = self.index >= len(self.data) - 1
        reward = 0
        exit_reason = "manual_close"

        if self.index < len(self.data):
            vec = self.get_feature_vector(self.data[self.index])
            self.history.append(np.nan_to_num(vec, nan=0.0, posinf=0.0, neginf=0.0))

        row = self.data[self.index]
        price = row.get("close", 0)

        if action == 0:
            reward = -0.001
        elif action in (1, 2) and self.position is None:
            reward = 0.05

        if self.position:
            reward += small_positional_bonus(self.position, row)

        if self.position and update_trailing_logic(self.position, row, stop_pct=TRAILING_STOP_PCT):
            action = 3
            exit_reason = "trailing_stop"

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
            self.position, row,
            decay_threshold=TRAILING_CONFIDENCE_DECAY,
            min_hold_minutes=MIN_HOLD_MINUTES,
            alpha=CONFIDENCE_SMOOTHING_ALPHA
        ):
            action = 3
            exit_reason = "confidence_decay"

        if action == 3 and self.position:
            entry = self.position["entry_price"]
            entry_conf = self.position.get("entry_confidence", 0)
            reward += (price - entry if self.position["direction"] == "long" else entry - price)
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
                f"[CLOSE] {self.token} | Action: {action} | Reward: {reward:.4f} | "
                f"Balance: {self.balance:.2f} | EntryConf: {entry_conf:.3f} | Reason: {exit_reason}"
            )
            self.position = None

        self.index += 1

        if self.index < len(self.data):
            self.history.append(self.get_feature_vector(self.data[self.index]))

        if done:
            self.logger.info(
                f"[CLOSE] {self.token} | Final Step | Reward: {reward:.4f} | Balance: {self.balance:.2f} | Reason: {exit_reason}"
            )
            return self._get_state(), reward, True, False, {}

        return self._get_state(), reward, False, False, {}
