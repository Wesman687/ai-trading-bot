'use client';
import { fetchAccounts } from '@/actions/accounts';
import AccountList from '@/components/ActionList';
import { useEffect } from 'react';
import { useDispatch } from 'react-redux';

export default function HomePage() {
  const dispatch = useDispatch();

  useEffect(() => {
    fetchAccounts()(dispatch);
  }, [dispatch]);
  

  return <AccountList />;
}


