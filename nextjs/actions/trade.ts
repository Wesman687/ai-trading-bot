import axios from 'axios';
import { AppDispatch } from '@/store/store';
import { setTradeHistory } from '@/store/tradesSlice';
import { API_BASE } from '@/lib/config';

export const fetchTradesByIds = (accountId: string, tradeIds: string[]) => async (dispatch: AppDispatch) => {
  try {
    const res = await axios.post(`${API_BASE}/account/${accountId}/trades`, { trade_ids: tradeIds });
    dispatch(setTradeHistory(res.data));
  } catch (err) {
    console.error('Failed to fetch trades:', err);
  }
};

export const fetchAllTrades = () => async (dispatch: AppDispatch) => {
  try {
    const res = await axios.get(`${API_BASE}/trades/`);
    dispatch(setTradeHistory(res.data)); // ✅ reuses your reducer
  } catch (err) {
    console.error('Failed to fetch all trades:', err);
  }
};