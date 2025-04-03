import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Trade } from '@/types/account';

interface TradesState {
  byId: Record<string, Trade>;
}

const initialState: TradesState = {
  byId: {},
};

const tradesSlice = createSlice({
  name: 'trades',
  initialState,
  reducers: {
    setTradeHistory(state, action: PayloadAction<Trade[]>) {
      action.payload.forEach((trade) => {
        state.byId[trade.trade_id] = trade;
      });
    },
  },
});

export const { setTradeHistory } = tradesSlice.actions;
export default tradesSlice.reducer;
