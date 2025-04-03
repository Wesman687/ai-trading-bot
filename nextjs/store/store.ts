// store.ts or store/index.ts
import { configureStore } from '@reduxjs/toolkit';
import accountsReducer from './accountsSlice';
import tradesReducer from './tradesSlice'
import { useDispatch } from 'react-redux';

export const store = configureStore({
  reducer: {
    accounts: accountsReducer,
    trades: tradesReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// ✅ Use this in components
export const useAppDispatch: () => AppDispatch = useDispatch;