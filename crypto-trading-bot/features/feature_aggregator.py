import numpy as np
import pandas as pd
from data.utils.convert_to_features import enrich_ohlcv
import pandas_ta as ta
from data.indicators import calculate_indicators
from data.ta_strat import ta_strategy
from data.final_features import compute_missing_feature
from data.utils.timeframes import convert_tf
from data.utils.timeframes import update_multi_tf_buffers

REQUIRED_ALWAYS = [
    "macd", "macd_cross", "macd_histogram", 
    "rsi", "sma_20", "ema_20",
    "volume_surge", "volume_vs_median", 
    "momentum_5", "doji_count", "trend_strength_5"
]

def aggregate_features(pair, features_history, latest_data, feature_names, candle_history):
    weighted = {}
    final_features = {}  # Store final features
    missing_features = []
    multi_tf_history = {}
    multi_tf_history = update_multi_tf_buffers(candle_history)
    tf_dfs = convert_tf(multi_tf_history)
    if len(features_history) < 30:
        print(f"[Aggregate] ⚠️ Not enough candles for {pair}. Only {len(features_history)} rows.")
        return {}
    required_features = list(set(feature_names + REQUIRED_ALWAYS))
    # --- Use the enriched 1-minute data directly
    df_1m = pd.DataFrame(features_history).copy()
    df_1m["timestamp"] = pd.to_datetime(df_1m["timestamp"], errors="coerce", utc=True)
    df_1m = df_1m.dropna(subset=["timestamp"]).set_index("timestamp").sort_index()

    try:
        # Directly use the enriched data (no need to re-enrich it)
        latest_enriched = df_1m.iloc[-2].to_dict()  # Get the last row (most recent data)
        weighted.update(latest_enriched)
    except Exception as e:
        print(f"[Aggregate] ❌ Failed to aggregate enriched data for {pair}: {e}")
    # --- Real-Time Additions ---
    weighted["realtime_close"] = latest_data.get("close", 0)
    weighted["realtime_volume"] = latest_data.get("volume", 0)
    weighted["wick_top_4h"] = latest_data.get("wick_top_4h", 0)
    # --- Final Feature Vector ---  
    
    base_df = pd.DataFrame(candle_history)
    base_df = base_df.copy()
    df_with_indicators = calculate_indicators(base_df)

    # Check for missing features
    for feature in required_features:
        if feature not in weighted and feature not in df_with_indicators.columns:
            missing_features.append(feature)

    # Fill known indicator-based features from df_with_indicators
    for feature in required_features:
        if feature in df_with_indicators.columns:
            final_features[feature] = df_with_indicators[feature].iloc[-1]
        elif feature in weighted:
            final_features[feature] = weighted[feature]

    # Fill multi-timeframe features using ta_strategy or fallback
    for feature in missing_features:
        # Try to infer timeframe (e.g., "rsi_4h" → "4h")
        for tf in tf_dfs:
            if feature.endswith(f"_{tf}"):
                df_tf = tf_dfs[tf]
                if df_tf is None or df_tf.empty:
                    print(f"⚠️ Skipping {feature} — empty {tf} data")
                    continue

                try:
                    val = ta_strategy(feature, df_tf, tf_name=tf)
                    if val is not None:
                        final_features[feature] = val
                        break
                except Exception as e:
                    print(f"❌ Error computing {feature} from {tf}: {e}")
        # Final fallback (logic-based)
        if feature not in final_features:
            compute_missing_feature(feature, weighted, base_df, final_features)
            
    return final_features