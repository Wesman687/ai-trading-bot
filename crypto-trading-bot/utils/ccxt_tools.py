import asyncio
import ccxt.async_support as ccxt


def create_binance():
    return ccxt.binance({
        "options": {
            "defaultType": "spot"
        }
    })


async def retry_fetch_ohlcv(exchange, pair, interval, limit, since=None, retries=3):
    for attempt in range(retries):
        try:
            return await exchange.fetch_ohlcv(pair, timeframe=interval, limit=limit, since=since)
        except Exception as e:
            print(f"⚠️ Retry {attempt+1}/{retries} failed: {e}")
            await asyncio.sleep(2)
    raise RuntimeError(f"❌ Failed to fetch OHLCV for {pair} after {retries} attempts.")



async def safe_close(exchange):
    try:
        await exchange.close()
    except Exception as e:
        print(f"⚠️ Failed to close exchange: {e}")