import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

def plot_prediction_distribution(token: str = "BTC"):
    token = token.upper()
    log_path = f"logs/predictions/{token}_predictions.csv"

    if not os.path.exists(log_path):
        print(f"❌ No log file found for {token}: {log_path}")
        return

    df = pd.read_csv(log_path, header=None)
    df.columns = ["timestamp", "token", "confidence", "threshold", "direction"]

    avg_threshold = df["threshold"].mean()

    # Plot histogram
    plt.figure(figsize=(10, 6))
    plt.hist(df["confidence"], bins=30, edgecolor="black", alpha=0.7)
    plt.axvline(avg_threshold, color="red", linestyle="--", label=f"Avg Threshold ({avg_threshold:.2f})")
    plt.title(f"{token} — Confidence Score Distribution")
    plt.xlabel("Confidence")
    plt.ylabel("Frequency")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # Direction counts
    print("\n📊 Direction Counts:")
    print(df["direction"].value_counts())

if __name__ == "__main__":
    token_arg = sys.argv[1] if len(sys.argv) > 1 else "BTC"
    plot_prediction_distribution(token_arg)
