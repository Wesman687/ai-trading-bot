'use client'
import { useEffect, useState } from 'react';
import axios from 'axios';

export default function AccountsList() {
  const [accounts, setAccounts] = useState([]);

  useEffect(() => {
    axios.get('/api/accounts')  // Proxy to FastAPI
      .then(res => setAccounts(res.data))
      .catch(err => console.error('Error fetching accounts:', err));
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">Accounts</h1>
      <ul>
        {accounts.map((acc: any) => (
          <li key={acc.account_id} className="mb-2">
            <a href={`/dashboard/accounts/${acc.account_id}`} className="text-blue-500 hover:underline">
              {acc.name || acc.account_id} → Balance: ${acc.balance.toFixed(2)}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
