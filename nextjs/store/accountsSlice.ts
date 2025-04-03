import { Account } from '@/types/account';
import { createSlice, PayloadAction } from '@reduxjs/toolkit';



interface AccountsState {
  byId: Record<string, Account>;
  allIds: string[];
  loading: boolean;
  error: string | null;
}

const initialState: AccountsState = {
  byId: {},
  allIds: [],
  loading: false,
  error: null,
};

const accountsSlice = createSlice({
  name: 'accounts',
  initialState,
  reducers: {
    fetchAccountsStart(state) {
      state.loading = true;
      state.error = null;
    },
    fetchAccountsSuccess(state, action: PayloadAction<Account[]>) {
      state.loading = false;
      const accounts = action.payload;
      state.byId = {};
      state.allIds = [];

      for (const account of accounts) {
        state.byId[account.account_id] = account;
        state.allIds.push(account.account_id);
      }
    },
    fetchAccountsFailure(state, action: PayloadAction<string>) {
      state.loading = false;
      state.error = action.payload;
    },
    updateAccount(state, action: PayloadAction<Account>) {
      const account = action.payload;
      state.byId[account.account_id] = account;
      if (!state.allIds.includes(account.account_id)) {
        state.allIds.push(account.account_id);
      }
    },
    removeAccount(state, action: PayloadAction<string>) {
      const id = action.payload;
      delete state.byId[id];
      state.allIds = state.allIds.filter((aid) => aid !== id);
    },
  },
});

export const {
  fetchAccountsStart,
  fetchAccountsSuccess,
  fetchAccountsFailure,
  updateAccount,
  removeAccount,
} = accountsSlice.actions;

export default accountsSlice.reducer;

