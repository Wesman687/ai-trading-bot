import { API_BASE } from '@/lib/config';
import {
    fetchAccountsStart,
    fetchAccountsSuccess,
    fetchAccountsFailure,
    updateAccount,
    removeAccount as deleteAccountFromState,
  } from '@/store/accountsSlice';
  import { AppDispatch } from '@/store/store';
import { Config } from '@/types/config';
import axios from 'axios';
  
  export const fetchAccounts = () => async (dispatch: AppDispatch) => {
    dispatch(fetchAccountsStart());
    try {
      const res = await axios.get(`${API_BASE}/account/`);
      dispatch(fetchAccountsSuccess(res.data));
    } catch (err: unknown) {
      if (err instanceof Error) {
        dispatch(fetchAccountsFailure(err.message));
        console.error('Failed to fetch accounts:', err);
      } else {
        console.error('An unknown error occurred:', err);
      }
    }
  };
  
  export const fetchAccountById = (accountId: string) => async (dispatch: AppDispatch) => {
    try {
      const res = await axios.get(`${API_BASE}/account/${accountId}`);
      dispatch(updateAccount(res.data));
    } catch (err) {
      console.error(`Failed to fetch account ${accountId}:`, err);
    }
  };
  
  // Update an account (e.g., config or metadata)
export const updateAccountConfig = (accountId: string, updatedData: Config) => async (dispatch: AppDispatch) => {
    try {
      const res = await axios.put(`${API_BASE}/account/${accountId}/config`, updatedData);
      dispatch(updateAccount(res.data));
    } catch (err) {
      console.error(`Failed to update account ${accountId}:`, err);
    }
  };
  
  // Delete an account
  export const deleteAccount = (accountId: string) => async (dispatch: AppDispatch) => {
    try {
      await axios.delete(`/account/${accountId}`);
      dispatch(deleteAccountFromState(accountId));
    } catch (err) {
      console.error(`Failed to delete account ${accountId}:`, err);
    }
  };