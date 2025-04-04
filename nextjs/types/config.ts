export interface ExitStrategy {
  min_hold_minutes: number;
  stop_loss_pct: number;
  trailing_stop_pct: number;
  volume_surge_min: number;
  macd_hist_max: number;
  macd_dir_max: number;
  rsi_reversal_required: boolean;
}

export interface FilterBase {
  min_trend: Record<"1m" | "15m" | "1h" | "1d", number>;
  doji_threshold: Record<"1m" | "15m" | "1h" | "1d", number>;
  noise_ratio_max: number;
}

export interface FilterMACDLong {
  rsi_min: number;
  macd_hist_min: number;
  macd_direction_min: number;
  volume_surge_min: number;
}

export interface FilterShortSetup {
  rsi_max: number;
  macd_hist_max: number;
  ema_20_buffer: number;
  sma_20_buffer: number;
  momentum_min: number;
  min_bearish_count: number;
}

export interface TokenConfig {
  auto_trade: boolean;
  trade_pct: number;
  confidence_thresholds: Record<'1m' | '15m' | '1h' | '1d', number>;
  filters: {
    base: FilterBase;
    macd_long: FilterMACDLong;
    short_setup: FilterShortSetup;
  };
  exit_strategy: ExitStrategy;
}

export type Timeframe = '1m' | '15m' | '1h' | '1d';
export type FilterKey = keyof TokenConfig['filters']; // 'base' | 'macd_long' | 'short_setup'
export type ExitStrategyKey = keyof ExitStrategy;
export type Config = Record<string, TokenConfig>; // e.g. BTC, SOL, XRP
