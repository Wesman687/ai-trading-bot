import hashlib
import json
import os
from pathlib import Path
import uuid
from datetime import  datetime, timedelta, timezone
from collections import deque

from matplotlib import pyplot as plt
import pandas as pd
from config import TRADE_CONFIG
from utils.logger import LOG_DIR, log, make_json_safe
from config import  HORIZON_WINDOWS

# Simulated wallet state
paper_trades = deque()

account = {
    "starting_balance": 10000.0,
    "balance": 10000.0,
    "trade_risk_pct": 0.15,
    "trade_size": 1000.0,
    "net_pnl": 0.0,
    "win_count": 0,
    "loss_count": 0,
    "trade_log": []
}

def get_adaptive_prediction_window(confidence):
    if confidence >= 0.9:
        return 15
    elif confidence >= 0.8:
        return 10
    return 5

def has_momentum_reversal(entry, current_price, direction):
    reverse_threshold = TRADE_CONFIG.get("reverse_momentum_pct", 0.005)
    if direction == "up" and current_price < entry * (1 - reverse_threshold):
        return True
    if direction == "down" and current_price > entry * (1 + reverse_threshold):
        return True
    return False

def simulate_trade(pair, direction, confidence, price, features=None, duration_minutes=15, multiplier=1.0):
    # Prevent duplicate open trades for the same pair
    for trade in reversed(paper_trades):
        if trade["pair"] == pair and not trade["evaluated"]:
            print(f"⚠️ Skipping duplicate trade for {pair} — still open.")
            return None

    # Risk management
    trade_risk_pct = TRADE_CONFIG.get("trade_risk_pct", 0.1)
    base_size = account["balance"] * trade_risk_pct
    adjusted_size = base_size * multiplier
    leverage = TRADE_CONFIG.get("leverage", 1)

    now = datetime.now(timezone.utc)
    trade = {
        "id": str(uuid.uuid4()),
        "pair": pair,
        "direction": direction,
        "confidence": float(confidence),
        "entry_price": price,
        "trade_size": adjusted_size,
        "timestamp": now.isoformat(),
        "check_after": (now + timedelta(minutes=duration_minutes)).isoformat(),
        "evaluated": False,
        "status": "open",
        "duration_minutes": duration_minutes,
        "features": features or {},
        "multiplier": multiplier,
        "peak_price": price,
        "peak_confidence": float(confidence),
    }

    log_prediction(
        pair=pair,
        direction=direction,
        confidence=confidence,
        success=None,
        price=price,
        features=features or {},
        reason="pending",
        exit_price=None,
        duration=duration_minutes,
        pnl=None,
        change=None
    )

    print(f"⚡️ Effective position: ${adjusted_size * leverage:.2f} (Leverage: {leverage}x | Multiplier: {multiplier}x)")
    print(f"🧪 Simulated {direction.upper()} trade for {pair} at ${price:.2f} | Hold: {duration_minutes}m | Size: ${adjusted_size:.2f}")    

    paper_trades.append(trade)
    return trade

from datetime import datetime, timedelta, timezone

def update_trade_outcomes(current_prices, predictions_by_horizon, pair):
    now = datetime.now(timezone.utc)

    for trade in list(paper_trades):
        if trade["evaluated"] or trade["pair"] != pair:
            continue

        current_price = current_prices.get(pair)
        if current_price is None:
            continue

        entry = trade["entry_price"]
        direction = trade["direction"]
        trade_size = trade["trade_size"]
        leverage = TRADE_CONFIG.get("leverage", 1)

        sl_pct = TRADE_CONFIG["stop_loss_pct"]
        tp_pct = TRADE_CONFIG["take_profit_pct"]

        sl_price = entry * (1 - sl_pct) if direction == "up" else entry * (1 + sl_pct)
        tp_price = entry * (1 + tp_pct) if direction == "up" else entry * (1 - tp_pct)

        entry_time = datetime.fromisoformat(trade["timestamp"])
        time_held = now - entry_time
        minutes_since_entry = time_held.total_seconds() / 60

        # Wait at least 10 seconds before evaluating
        if time_held.total_seconds() < 10:
            continue

        duration = trade.get("duration_minutes", 15)
        remaining_time = duration - minutes_since_entry

        # Filter prediction horizons based on time left
        valid_horizons = [h for h in predictions_by_horizon if HORIZON_WINDOWS[h] <= remaining_time]
        confidence = max(
            (predictions_by_horizon[h].get("confidence", 0) for h in valid_horizons),
            default=0
        )        

        early_exit, reason = should_exit_trade(trade, current_price, confidence, time_held, sl_price, tp_price)

        # Optional soft timeout cleanup logic (disabled by default)
        if not early_exit and time_held >= timedelta(minutes=duration * 2) and confidence < 0.4:
            early_exit, reason = True, "long_hold_low_confidence"

        if not early_exit:
            continue  # ⏳ Keep trade open if no exit reason yet

        # Evaluate outcome
        won = (
            (direction == "up" and current_price > entry) or
            (direction == "down" and current_price < entry)
        )

        # Calculate PnL
        change = (current_price - entry) / entry
        pnl = trade_size * change * leverage

        # Final record updates
        account["balance"] += pnl
        account["net_pnl"] += pnl
        account["win_count" if won else "loss_count"] += 1

        trade_result = {
            "id": trade["id"],
            "pair": trade["pair"],
            "timestamp": trade["timestamp"],
            "entry": entry,
            "exit_price": current_price,
            "exit_time": now.isoformat(),
            "direction": direction,
            "won": won,
            "pnl": round(pnl, 2),
            "reason": reason or "n/a",
            "duration": trade.get("duration_minutes")
        }

        log_trade_result({
            **trade_result,
            "confidence": trade["confidence"],
            "change_pct": round(change * 100, 2),
            "features": trade.get("features", {})
        })

        trade["evaluated"] = True
        trade["status"] = "closed"
        account["trade_log"].append(trade_result)

        export_account_snapshot()
        log_full_trade(trade_result, stage="closed")

        print(f"📈 Trade {direction.upper()} | {pair} | Result: {'WIN' if won else 'LOSS'} | Reason: {reason} | PnL: ${pnl:.2f}")

def should_exit_trade(trade, current_price, confidence, time_held, sl_price, tp_price):
    min_hold = timedelta(minutes=5)
    optimal_exit = timedelta(minutes=trade["duration_minutes"] // 2)

    direction = trade["direction"]
    features = trade.get("features", {})
    rsi_reversal = features.get("rsi_reversal", False)
    macd_hist = features.get("macd_histogram", 0)
    macd_dir = features.get("macd_direction_3", 0)
    volume_surge = features.get("volume_surge", 1)

    trailing_conf = trade.get("peak_confidence", confidence)
    trailing_price = trade.get("peak_price", current_price)

    # Trailing stop logic
    price_drop_pct = (trailing_price - current_price) / trailing_price if direction == "up" else (current_price - trailing_price) / trailing_price
    confidence_drop = trailing_conf - confidence

    if time_held < min_hold:
        return False, None

    if price_drop_pct > 0.01:
        return True, "trailing_stop"
    if confidence_drop > 0.1 and time_held > optimal_exit:
        return True, "confidence_decay"
    if direction == "up" and current_price <= sl_price:
        return True, "stop_loss"
    if direction == "up" and current_price >= tp_price:
        return True, "take_profit"
    if direction == "down" and current_price >= sl_price:
        return True, "stop_loss"
    if direction == "down" and current_price <= tp_price:
        return True, "take_profit"
    if rsi_reversal or (macd_hist < 0 and macd_dir < 0) or volume_surge < 0.8:
        return True, "momentum_decay"

    return False, None

def check_trailing_logic(trade, current_price, confidence, direction):
    """
    Evaluates trailing stop loss and trailing confidence drop.
    Updates peak values stored in the trade object.
    Returns (should_exit: bool, reason: str)
    """
    trail_stop_pct = TRADE_CONFIG.get("trailing_stop_pct", 0.01)
    trail_conf_pct = TRADE_CONFIG.get("trailing_confidence_pct", 0.2)

    # Update peak price
    if direction == "up":
        trade["peak_price"] = max(trade.get("peak_price", current_price), current_price)
        trail_price = trade["peak_price"] * (1 - trail_stop_pct)
        if current_price < trail_price:
            return True, "trailing_stop"
    elif direction == "down":
        trade["peak_price"] = min(trade.get("peak_price", current_price), current_price)
        trail_price = trade["peak_price"] * (1 + trail_stop_pct)
        if current_price > trail_price:
            return True, "trailing_stop"

    # Update peak confidence
    trade["peak_confidence"] = max(trade.get("peak_confidence", confidence), confidence)
    if confidence < trade["peak_confidence"] * (1 - trail_conf_pct):
        return True, "trailing_confidence"

    return False, None

def plot_trade_history(pair, price_history, trades):
    df = pd.DataFrame(price_history)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.set_index("timestamp", inplace=True)

    plt.figure(figsize=(12, 6))
    plt.plot(df["close"], label="Price", linewidth=2)

    for trade in trades:
        if trade["pair"] != pair:
            continue
        entry_time = pd.to_datetime(trade["timestamp"])
        exit_time = pd.to_datetime(trade["exit_time"])
        plt.axvline(entry_time, color='green' if trade["won"] else 'red', linestyle="--", alpha=0.6)
        plt.axvline(exit_time, color='black', linestyle=":", alpha=0.5)
        plt.scatter(entry_time, trade["entry"], color='blue', label='Entry' if 'Entry' not in plt.gca().get_legend_handles_labels()[1] else "")
        plt.scatter(exit_time, trade["exit_price"], color='orange', label='Exit' if 'Exit' not in plt.gca().get_legend_handles_labels()[1] else "")

    plt.title(f"Trade History for {pair}")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def log_full_trade(trade_data, stage="open", path="logs/trade_history.jsonl"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    safe_data = make_json_safe(trade_data)
    with open(path, "a") as f:
        f.write(json.dumps(safe_data) + "\n")
        

def log_trade_result(trade_result: dict):
    log_path = Path(LOG_DIR) / "trade_results.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    safe_result = make_json_safe(trade_result)

    with open(log_path, "a") as f:
        f.write(json.dumps(safe_result) + "\n")


_last_snapshot_hash = None
_last_logged_minute = None

def log_live_account_status(current_prices):
    global _last_snapshot_hash, _last_logged_minute

    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)  # ⏱️ round to nearest minute

    if _last_logged_minute == now:
        return  # already logged for this minute

    # Build snapshot dict
    snapshot = {
        "timestamp": now.isoformat(),
        "balance": round(account["balance"], 2),
        "net_pnl": round(account["net_pnl"], 2)
    }

    for pair, price in current_prices.items():
        snapshot[f"price_{pair.replace('/', '_')}"] = price

    # Add open trades info
    open_trades = [t for t in paper_trades if not t["evaluated"]]
    snapshot["open_trades"] = len(open_trades)
    snapshot["risk_exposure"] = round(sum(t["trade_size"] for t in open_trades), 2)

    # Hash the snapshot to check for changes
    snapshot_str = json.dumps(snapshot, sort_keys=True)
    snapshot_hash = hashlib.md5(snapshot_str.encode()).hexdigest()

    if snapshot_hash == _last_snapshot_hash:
        return  # nothing changed, skip logging

    # ✅ Log it
    log_path = "logs/live_account.jsonl"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    with open(log_path, "a") as f:
        f.write(snapshot_str + "\n")

    _last_snapshot_hash = snapshot_hash
    _last_logged_minute = now
    
_last_snapshot_time = {}       

def log_live_account(current_prices):
    entry = {
        "timestamp": datetime.now(timezone.utc),
        "balance": account["balance"],
        "net_pnl": account["net_pnl"]
    }
    for pair, price in current_prices.items():
        token = pair.replace("/", "_")
        entry[f"price_{token}"] = price

    with open("logs/live_account.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")
        
def log_live_snapshot(pair=None, price=None, interval_seconds=60):
    global _last_snapshot_time
    now = datetime.utcnow()
    last = _last_snapshot_time.get(pair)
    if last and (now - last).total_seconds() < interval_seconds:
        return  # Skip until time threshold passes
    _last_snapshot_time[pair] = now
    snapshot = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "balance": round(account["balance"], 2),
        "net_pnl": round(account["net_pnl"], 2),
        "open_trades": len([t for t in paper_trades if not t["evaluated"]]),
        "win_count": account["win_count"],
        "loss_count": account["loss_count"],
        "pair": pair,
        "current_price": price,
    }

    log_path = "logs/live_account_snapshots.jsonl"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    with open(log_path, "a") as f:
        f.write(json.dumps(snapshot) + "\n")


def export_trades_to_csv(path="logs/paper_trades.csv"):
    df = pd.DataFrame(account["trade_log"])
    df.to_csv(path, index=False)
    print(f"📤 Exported trade log to {path}")

def export_account_snapshot(path="logs/account_snapshot.json"):
    snapshot = {
        "balance": round(account["balance"], 2),
        "net_pnl": round(account["net_pnl"], 2),
        "wins": account["win_count"],
        "losses": account["loss_count"],
        "win_rate": round(
            account["win_count"] / (account["win_count"] + account["loss_count"]), 4
        ) if (account["win_count"] + account["loss_count"]) > 0 else 0.0
    }

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(snapshot, f, indent=2)
            
def log_prediction(pair, direction, confidence, success, price=None, features=None, reason=None, exit_price=None, duration="15min", pnl=None, change=None):
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pair": pair,
        "direction": direction,
        "confidence": float(confidence),
        "success": success,
        "entry_price": price,
        "exit_price": exit_price,
        "pnl": round((exit_price - price), 4) if success and price and exit_price else None,
        "features": features or {},
        "reason": reason,
        "pnl": pnl,
        "change": change
    }

    log_path = "logs/prediction_history.jsonl"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    with open(log_path, "a") as f:
        safe_entry = make_json_safe(log_entry)
        f.write(json.dumps(safe_entry) + "\n")
        
def export_open_trades(path="logs/open_trades.json"):
    open_trades = [t for t in paper_trades if not t["evaluated"]]
    with open(path, "w") as f:
        json.dump(open_trades, f, indent=2, default=str)