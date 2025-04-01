import math

import numpy as np
from utils.logger import log_confidence
from config import STRATEGY_CONFIG, HORIZON_WINDOWS, MIN_TREND

from datetime import timedelta





def calculate_hold_duration(horizon: str, confidence: float, features: dict) -> int:
    base_minutes = {
        "1m": 5,
        "15m": 15,
        "1h": 60,
        "1d": 240
    }.get(horizon, 15)

    # --- Confidence Boost ---
    if confidence >= 0.95:
        base_minutes *= 2
    elif confidence >= 0.9:
        base_minutes *= 1.3
    elif confidence >= 0.85:
        base_minutes *= 1.15
    elif confidence < 0.75:
        base_minutes *= 0.75

    # --- Trend Strength ---
    trend = features.get("trend_strength_5", 1)
    if trend > 1.5:
        base_minutes *= 1.3
    elif trend < 0.5:
        base_minutes *= 0.7

    # --- MACD Momentum ---
    macd_hist = features.get("macd_histogram", 0)
    macd_dir = features.get("macd_direction_3", 0)
    if macd_dir > 0 and macd_hist > 0:
        base_minutes *= 1.2
    elif macd_dir < 0 or macd_hist < 0:
        base_minutes *= 0.8

    # --- Volume Surge ---
    volume_surge = features.get("volume_surge", 1)
    if volume_surge > 2:
        base_minutes *= 1.2
    elif volume_surge < 1:
        base_minutes *= 0.8

    # --- Clamp to sane values ---
    return int(max(3, min(base_minutes, 240)))  # 3m–4h max

def evaluate_multi_signal(predictions_by_horizon, token, feature_sets_by_horizon, price):
    HORIZONS = ["1m", "15m", "1h", "1d"]
    strategy = STRATEGY_CONFIG.get(token.upper(), {})
    CONF_THRESHOLDS = strategy.get("confidence_thresholds", {
        "1m": 0.85, "15m": 0.8, "1h": 0.75, "1d": 0.7
    })
    override_threshold = strategy.get("confidence_override_threshold", 0.95)

    stacked_signals = []
    last_direction = None
    low_confidences = []
    high_confidences = []
    base_filter_failures = []

    stacking_valid = True

    for horizon in HORIZONS:
        prediction = predictions_by_horizon.get(horizon)
        features = feature_sets_by_horizon.get(horizon)
        if not prediction or not features:
            continue

        confidence = prediction.get("confidence", 0)
        direction = prediction.get("direction")
        threshold = CONF_THRESHOLDS.get(horizon, 0.75)

        # Track all confidences
        if confidence >= threshold:
            high_confidences.append((horizon, confidence))
        else:
            low_confidences.append((horizon, confidence))

        # Base filter checks
        passed, failures = base_filters(features, horizon)
        if not passed:
            base_filter_failures.append((horizon, failures))

        valid = False
        if stacking_valid:
            if direction != last_direction and last_direction is not None:
                print(f"[{horizon}] ❌ Direction mismatch: {direction} vs {last_direction}")
                stacking_valid = False
                continue

            if confidence >= threshold or confidence >= override_threshold:
                if direction == "up" and features.get("macd_cross") == 1:
                    if validate_macd_long(features):
                        valid = True
                elif direction == "down":
                    if validate_short_setup(features):
                        valid = True
                elif confidence >= override_threshold:
                    print(f"[{horizon}] ⚠️ Overriding filters due to high confidence: {confidence:.2f}")
                    valid = True

            if valid:
                stacked_signals.append((horizon, direction, confidence))
                last_direction = direction
            else:
                stacking_valid = False

    # Always show confidence summary
    if low_confidences:
        low_str = " | ".join(f"{h}:{c:.2f}" for h, c in low_confidences)
        print(f"❌ {token} {direction}  Low Confidences → {low_str}")

    if high_confidences:
        high_str = " | ".join(f"{h}:{c:.2f}" for h, c in high_confidences)
        print(f"✅{token} {direction} High Confidences → {high_str}")

    if not stacked_signals:
        if base_filter_failures:
            print("❌ Base filter issues (truncated):")
            for horizon, fails in base_filter_failures[:2]:
                print(f"  - {horizon}: {', '.join(fails)}")
            if len(base_filter_failures) > 2:
                print(f"  ...and {len(base_filter_failures) - 2} more")
        return None

    if not stacked_signals:
        if base_filter_failures:
            print("❌ Base filter issues (truncated):")
            for horizon, fails in base_filter_failures[:2]:
                print(f"  - {horizon}: {', '.join(fails)}")
            if len(base_filter_failures) > 2:
                print(f"  ...and {len(base_filter_failures) - 2} more")
        return None

    # Now it's safe to use stacked_signals[-1]
    best_signal = stacked_signals[-1]
    horizon, direction, confidence = best_signal
    features = feature_sets_by_horizon[horizon]

    duration_minutes = calculate_hold_duration(horizon, confidence, features)

    avg_conf = np.mean([c for _, c in high_confidences])
    num_high = len(high_confidences)
    multiplier = (
        3.0 if num_high >= 4 and avg_conf >= 0.9 else
        2.0 if num_high >= 3 and avg_conf >= 0.85 else
        1.5 if num_high >= 2 and avg_conf >= 0.8 else
        1.0
    )

    print(f"✅ Confirmed up to {horizon} | Direction: {direction.upper()} | Confidence: {confidence:.3f}")
    print(f"🔁 Confidence Multiplier: {multiplier:.2f}")

    return {
        "direction": direction,
        "confidences": predictions_by_horizon,
        "confidence": predictions_by_horizon.get("15m", {}).get("confidence", 0),
        "horizon": horizon,
        "duration": duration_minutes,
        "features": features,
        "multiplier": multiplier,
        "price": price
    }

def doji_threshold_for(horizon):
    return {
        "1m": 5,
        "15m": 4,
        "1h": 3,
        "1d": 2,
    }.get(horizon, 4)

def base_filters(features, horizon="1m"):
    failures = []

    doji_count = features.get("doji_count", 0)
    trend_strength = features.get("trend_strength_5", 1)
    noise_ratio = features.get("noise_ratio", 0)

    # Smarter doji filter: Only fail if both doji_count is high AND trend is weak
    if doji_count > doji_threshold_for(horizon) and trend_strength < MIN_TREND.get(horizon, 0.4):
        failures.append(f"high doji_count: {doji_count}, weak trend: {trend_strength}")

    if noise_ratio > 0.75:
        failures.append(f"high noise ratio: {noise_ratio}")

    if trend_strength < MIN_TREND.get(horizon, 0.4):
        failures.append(f"weak trend: {trend_strength}")

    if failures:
        return False, failures
    return True, []

def validate_macd_long(features, debug=False):
    """
    Validates if MACD long setup is strong enough.
    Conditions:
    - RSI above 50 and rising
    - Strong volume
    - MACD histogram positive (momentum building)
    - MACD direction rising
    """
    failures = []

    # RSI strength
    if features.get("rsi", 0) <= 50 or features.get("rsi_direction_3", 0) <= 0.66:
        failures.append("weak RSI direction")

    # Volume strength
    if features.get("volume_surge", 0) <= 1.2 and features.get("volume_vs_median", 0) <= 1.2:
        failures.append("weak volume")

    # MACD momentum
    if features.get("macd_histogram", 0) <= 0:
        failures.append("bearish MACD histogram")

    # MACD direction (should be rising)
    if features.get("macd_direction_3", 0) <= 0:
        failures.append("MACD direction not rising")

    if failures:
        if debug:
            print("[Filter] Skipping MACD long setup due to:", "; ".join(failures))
        return False

    return True

def validate_short_setup(features):
    failures = []
    if features.get("rsi_cross_50", 1) == 1:
        failures.append("RSI above 50")
    if features.get("macd_histogram", 0) >= 0:
        failures.append("MACD histogram not bearish")
    if features.get("ema_20", 0) >= features.get("ema_20_prev", 1e9):
        failures.append("EMA20 not dropping")
    if features.get("sma_20", 0) >= features.get("sma_20_prev", 1e9):
        failures.append("SMA20 not dropping")
    if features.get("momentum_5", 0) >= -0.0025:
        failures.append("momentum too weak")
    if features.get("bearish_count_5", 0) < 3:
        failures.append("bearish count too low")

    if failures:
        print("[Filter] Skipping short setup due to:", "; ".join(failures))
        return False
    return True