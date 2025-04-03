import { createSelector } from '@reduxjs/toolkit';
import { RootState } from '@/store/store';

export const selectAccountById = (id: string) =>
  createSelector(
    (state: RootState) => state.accounts.byId,
    (byId) => byId[id]
  );

export const selectAllAccounts = createSelector(
  (state: RootState) => state.accounts.allIds,
  (state: RootState) => state.accounts.byId,
  (ids, byId) => ids.map((id) => byId[id])
);