# dashboard.py
import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
from trading.paper_wallet import plot_trade_history

import os
from config import WATCHED_PAIRS

PREDICTION_LOG = "logs/prediction_history.jsonl"
ACCOUNT_SNAPSHOT = "logs/account_snapshot.json"
LIVE_ACCOUNT_LOG = "logs/live_account.jsonl"

def load_history():
    if not os.path.exists(PREDICTION_LOG):
        return pd.DataFrame()

    try:
        with open(PREDICTION_LOG, "r") as f:
            if PREDICTION_LOG.endswith(".jsonl"):
                lines = f.readlines()
                data = [json.loads(line.strip()) for line in lines if line.strip()]
            else:
                data = json.load(f)
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Failed to load prediction history: {e}")
        return pd.DataFrame()

def load_account_snapshot():
    if not os.path.exists(ACCOUNT_SNAPSHOT):
        return {}
    with open(ACCOUNT_SNAPSHOT, "r") as f:
        return json.load(f)

def load_live_account():
    if not os.path.exists(LIVE_ACCOUNT_LOG):
        return pd.DataFrame()
    with open(LIVE_ACCOUNT_LOG, "r") as f:
        lines = f.readlines()
        records = [json.loads(line.strip()) for line in lines if line.strip()]
    return pd.DataFrame(records)

def load_open_trades(path="logs/open_trades.json"):
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)
def load_price_history(pair):
    path = f"logs/price_history/{pair.replace('/', '_')}.jsonl"
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return [json.loads(line.strip()) for line in f if line.strip()]

def show_open_trades():
    trades = load_open_trades()
    if not trades:
        st.info("No open trades currently.")
        return

    st.subheader("📂 Open Trades")
    df = pd.DataFrame(trades)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    st.dataframe(df, use_container_width=True)

def analyze(df):
    if df.empty:
        st.warning("No prediction data found.")
        return

    wins = df[df['success'] == True].shape[0]
    losses = df[df['success'] == False].shape[0]
    win_rate = wins / (wins + losses) if (wins + losses) else 0
    snapshot = load_account_snapshot()

    st.subheader("💰 Account Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Balance", f"${snapshot.get('balance', 0):,.2f}")
    col2.metric("Net PnL", f"${snapshot.get('net_pnl', 0):,.2f}")
    col3.metric("Wins", snapshot.get("wins", 0))
    col4.metric("Losses", snapshot.get("losses", 0))
    col5, col6 = st.columns(2)
    col5.metric("📊 Historical Win Rate", f"{win_rate * 100:.1f}%")
    col6.metric("📂 Snapshot Win Rate", f"{snapshot.get('win_rate', 0) * 100:.1f}%")

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['success'] = df['success'].fillna("unknown")

    st.write("## Prediction Overview")
    st.dataframe(df.tail(100), use_container_width=True)

    st.write("### Win/Loss Ratio")
    st.bar_chart(df['success'].value_counts())

    st.write("### Confidence Distribution")
    st.bar_chart(df['confidence'])

    st.write("### Per Token Summary")
    for pair in WATCHED_PAIRS:
        token_df = df[df['pair'] == pair]
        st.subheader(pair)
        st.write(f"Total Predictions: {len(token_df)}")
        st.bar_chart(token_df['direction'].value_counts())
        st.line_chart(token_df.set_index('timestamp')['confidence'])
        price_data = load_price_history(pair)
        if price_data:
            st.write("📈 Trade History")
            fig = plt.figure()
            plot_trade_history(pair, price_data, df[df["pair"] == pair].to_dict("records"))
            st.pyplot(fig)
        else:
            st.info(f"No price history found for {pair}")
        
    fig, ax = plt.subplots()
    ax.hist(df['confidence'], bins=20, color='skyblue', edgecolor='black')
    ax.set_title("Confidence Distribution")
    ax.set_xlabel("Confidence")
    ax.set_ylabel("Count")
    st.pyplot(fig)
    show_open_trades()

def plot_live_account():
    df = load_live_account()
    if df.empty:
        st.warning("No live account data found.")
        return

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')
    st.subheader("📈 Live Balance and PnL Over Time")
    st.line_chart(df[['balance', 'net_pnl']])

    if 'price_SOL_USDT' in df.columns:
        st.subheader("📊 Live Price Tracking")
        st.line_chart(df[[col for col in df.columns if col.startswith("price_")]])
        
        

st.set_page_config(page_title="Crypto Bot Dashboard", layout="wide")
st.title("📊 Crypto AI Prediction Dashboard")

df = load_history()
analyze(df)

plot_live_account()
