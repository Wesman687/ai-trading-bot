import { Config } from './config';

export interface Account {
  _id: string;
  account_id: string;
  name: string;
  starting_balance: number;
  available_balance: number;
  leverage: number;
  trade_risk_pct: number;
  balance: number;
  net_pnl: number;
  win_count: number;
  trade_size: number;
  loss_count: number;
  performance: [];
  open_trades: Trade[];
  trade_log: Trade[];
  open_trade_ids: string[];
  closed_trade_ids: string[];
  tokens: tokenAccountStats[]
  config: Config;
}
export interface tokenAccountStats {
  win: number;
  loss: number;
  pnl: number;
}
export interface Trade {
  trade_id: string;
  account_id: string;
  account_ref: string;
  token: string;
  direction: string;
  entry_price: number;
  confidence: number;
  status: string;
  current_price: number;
  current_pnl: number;
  leverage: number;
  trade_size: number;
  entry_time: string;
  exit_time?: string;
  exit_price?: number;
  reason: string;
  pnl: number;
}