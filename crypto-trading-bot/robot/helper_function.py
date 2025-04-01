# helper_functions.py

from datetime import datetime
from config import STRATEGY_CONFIG

def update_trailing_logic(position, row, stop_pct=0.01):
    price = row.get("close", 0)
    direction = position["direction"]

    if direction == "long":
        position["peak_price"] = max(position.get("peak_price", price), price)
        if price < position["peak_price"] * (1 - stop_pct):
            return True  # trigger exit
    elif direction == "short":
        position["bottom_price"] = min(position.get("bottom_price", price), price)
        if price > position["bottom_price"] * (1 + stop_pct):
            return True  # trigger exit
    return False

def apply_confidence_decay(position, row, decay_threshold=0.2, min_hold_minutes=3, alpha=0.8):
    current_conf = row.get("confidence", 1.0)
    prev_smooth = position.get("smoothed_confidence", current_conf)
    smoothed = alpha * prev_smooth + (1 - alpha) * current_conf
    position["smoothed_confidence"] = smoothed

    decay_trigger = position["entry_confidence"] * (1 - decay_threshold)
    entry_time = datetime.fromisoformat(position["entry_time"])
    now = datetime.fromisoformat(row.get("timestamp")) if "timestamp" in row else datetime.now()
    hold_minutes = (now - entry_time).total_seconds() / 60

    if hold_minutes >= min_hold_minutes and smoothed < decay_trigger:
        return True  # trigger exit
    return False

def compute_extended_reward(token, position, row, base_reward):
    bonus = 0.0
    confidence = row.get("confidence", 1.0)
    hold_duration = (datetime.fromisoformat(row["timestamp"]) - datetime.fromisoformat(position["entry_time"])).total_seconds() / 60

    # 1. Early exit bonus
    if base_reward > 0 and hold_duration < position["duration_minutes"] * 0.5:
        bonus += 0.5

    # 2. Low-confidence penalty
    threshold = STRATEGY_CONFIG.get(position.get("token", ""), {}).get("confidence_thresholds", {}).get("1m", 0.75)
    if position["entry_confidence"] < threshold + 0.05:
        bonus -= 0.5

    return bonus

def shape_reward_with_duration(position, current_row, base_reward):
    try:
        entry_time = datetime.fromisoformat(position.get("entry_time"))
        now = datetime.fromisoformat(current_row.get("timestamp")) if "timestamp" in current_row else datetime.now()
        hold_minutes = (now - entry_time).total_seconds() / 60
        duration_target = position.get("duration_minutes", 5)

        if base_reward > 0 and hold_minutes < duration_target:
            return base_reward * 1.1  # Bonus for quick wins
        elif base_reward < 0 and hold_minutes < duration_target:
            return base_reward * 1.2  # Penalty for bad early exits
    except Exception as e:
        print(f"[WARN] Reward shaping failed: {e}")
    
    return base_reward  # fallback