import { Config } from './config';

export interface Account {
  account_id: string;
  name: string;
  balance: number;
  net_pnl: number;
  win_count: number;
  loss_count: number;
  performance: [];
  open_trades: Trade[];
  trade_log: Trade[];
  open_trade_ids: string[];
  config: Config;
}
export interface Trade {
  trade_id: string;
  token: string;
  direction: string;
  entry_price: number;
  confidence: number;
  status: string;
  trade_size: number;
  entry_time: string;
  exit_time?: string;
  exit_price?: number;
  pnl: number;
}