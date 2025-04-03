'use client';
import { fetchAccounts } from '@/actions/accounts';
import { fetchAllTrades } from '@/actions/trade';
import AccountList from '@/components/ActionList';
import { useAppDispatch } from '@/store/store';
import { useEffect } from 'react';

export default function HomePage() {
  const dispatch = useAppDispatch(); // ✅ correct hook

  useEffect(() => {
    dispatch(fetchAccounts()); // ✅ works now
    dispatch(fetchAllTrades()); // ✅ works now
    const interval = setInterval(() => {
      dispatch(fetchAllTrades());
      dispatch(fetchAccounts());
    }, 60_000); // 1 min polling

    return () => clearInterval(interval);
  }, [dispatch]);
  

  return <AccountList />;
}


