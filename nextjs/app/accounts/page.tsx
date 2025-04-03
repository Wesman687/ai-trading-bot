'use client';

import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchAccounts } from '@/actions/accounts';
import { RootState } from '@/store/store';
import { useRouter } from 'next/navigation';

export default function AccountsList() {
  const dispatch = useDispatch();
  const router = useRouter();
  const accounts = useSelector((state: RootState) => state.accounts.allIds.map(id => state.accounts.byId[id]));

  useEffect(() => {
    fetchAccounts();
  }, [dispatch]);

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">Accounts</h1>
      <ul>
        {accounts.map((acc) => (
          <li
            key={acc.account_id}
            className="mb-2 cursor-pointer hover:text-blue-500"
            onClick={() => router.push(`/account/${acc.account_id}`)}
          >
            {acc.name || acc.account_id} → Balance: ${acc.balance.toFixed(2)}
          </li>
        ))}
      </ul>
    </div>
  );
}
