// selectors/accountSelectors.ts
import { createSelector } from '@reduxjs/toolkit';
import { RootState } from '../store';

export const selectTradeLogForAccount = (accountId: string) =>
  createSelector(
    (state: RootState) => state.accounts.byId[accountId],
    (state: RootState) => state.trades.byId,
    (account, tradesById) =>
      account?.closed_trade_ids?.map(id => tradesById[id]).filter(Boolean) || []
  );