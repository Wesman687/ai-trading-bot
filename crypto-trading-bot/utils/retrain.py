import asyncio
from datetime import datetime, timezone
import os
from config import    HORIZONS,  WATCHED_PAIRS

async def retrain_daily():
    while True:
        now = datetime.now(timezone.utc)
        if now.hour == 1 and now.minute == 0:
            print("⏳ [Retrain] Starting daily retraining...")

            for pair in WATCHED_PAIRS:
                token = pair.split("/")[0].upper()

                # ✅ Step 1: Refresh 7-day split data
                print(f"🔄 [Retrain] Refreshing 7-day history for {token}")

                # ✅ Step 2: Aggregate all 7d CSVs into a training file
                daily_dir = "data/daily"
                csv_out = f"data/logs/{token}USDT_ohlcv.csv"
                with open(csv_out, "w") as outfile:
                    header_written = False
                    for filename in sorted(os.listdir(daily_dir)):
                        if filename.startswith(f"{token}USDT_1m") and filename.endswith(".csv"):
                            with open(os.path.join(daily_dir, filename), "r") as infile:
                                lines = infile.readlines()
                                if not header_written:
                                    outfile.write(lines[0])  # write header once
                                    header_written = True
                                outfile.writelines(lines[1:])  # skip header after first
                    

                # ✅ Step 3: Run training
                cmd = f"python model/train_local.py --csv {csv_out} --token {token}"
                print(f"📦 [Retrain] Running: {cmd}")
                exit_code = os.system(cmd)

                if exit_code == 0:
                    print(f"✅ [Retrain] {token} training completed.")
                else:
                    print(f"❌ [Retrain] {token} failed with exit code {exit_code}")

            await asyncio.sleep(60)  # wait 1 minute so it doesn’t double run
        else:
            await asyncio.sleep(30)
