from btcc_trader import place_market_order, get_balance

get_balance()

place_market_order("BTCUSDT", "buy", 0.001)  # dry-run by default
