import pandas as pd
from collections import defaultdict

# ✅ Define this once where you know all required model input features



def group_missing_features(missing):
    grouped = defaultdict(list)
    for f in missing:
        if any(tf in f for tf in ["_1m"]):
            grouped["1m"].append(f)
        elif any(tf in f for tf in ["_5", "_5min"]):
            grouped["5m"].append(f)
        elif "_15" in f:
            grouped["15m"].append(f)
        elif "_1h" in f:
            grouped["1h"].append(f)
        elif "_4h" in f:
            grouped["4h"].append(f)
        elif any(x in f for x in ["_1d", "_day"]):
            grouped["1d"].append(f)
        else:
            grouped["base"].append(f)
    return grouped
