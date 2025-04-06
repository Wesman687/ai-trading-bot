
import { Config, TokenConfig } from "@/types/config";

export const createDefaultTokenConfig = (): TokenConfig => ({
  auto_trade: true,
  trade_pct: 0.2,
  confidence_thresholds: {
    "1m": 0.85,
    "15m": 0.82,
    "1h": 0.78,
    "1d": 0.75,
  },
  filters: {
    base: {
      min_trend: { "1m": 0.05, "15m": 0.08, "1h": 0.1, "1d": 0.12 },
      doji_threshold: { "1m": 5, "15m": 4, "1h": 2, "1d": 1 },
      noise_ratio_max: 0.68,
    },
    macd_long: {
      rsi_min: 50,
      macd_hist_min: 0.01,
      macd_direction_min: 0.01,
      volume_surge_min: 1.2,
    },
    short_setup: {
      rsi_max: 58,
      macd_hist_max: -0.01,
      ema_20_buffer: 0.01,
      sma_20_buffer: 0.01,
      momentum_min: -0.1,
      min_bearish_count: 3,
    },
  },
  exit_strategy: {
    stop_loss_pct: 0.03,
    trailing_stop_pct: 0.015,
    rsi_reversal_required: false,
    macd_hist_max: 0,
    macd_dir_max: 0,
    volume_surge_min: 0.8,
    min_hold_minutes: 5,
  },
});

export const createDefaultConfig = (tokens: string[]): Config => {
  const config: Config = {};
  for (const token of tokens) {
    config[token] = createDefaultTokenConfig();
  }
  return config;
};