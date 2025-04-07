'use client'

import { useRouter } from 'next/navigation';
import { useMemo, useState } from 'react';
import { toast } from 'sonner';
import TokenConfigEditor from '@/components/TokenConfigEditor';
import { Button } from '@/components/ui/button';
import { createDefaultConfig } from '@/utils/defaultConfig';
import { useSelector } from 'react-redux';
import { RootState } from '@/store/store';
import { API_BASE } from '@/lib/config';
import { selectAllAccounts } from '@/store/selectors/account';

export default function CreateAccountPage() {
  const router = useRouter();

  const [account, setAccount] = useState({
    name: 'New Account',
    leverage: 1.5,
    starting_balance: 10000,
  });
  const tokens = useSelector((state: RootState) => state.accounts.availableTokens);
  const defaultConfig = createDefaultConfig(tokens);
  const [config, setConfig] = useState(() => defaultConfig);
  const memoizedSelector = useMemo(() => selectAllAccounts, []);
  const accounts = useSelector(memoizedSelector);
  const [copyFromId, setCopyFromId] = useState<string | null>(null);

  const handleCopyConfig = (id: string) => {
    const fromAccount = accounts.find(acc => acc._id === id);
    if (fromAccount) {
      setConfig(fromAccount.config);
    }
  };
  const handleSubmit = async () => {
    const paylog = {
      name: account.name,
      leverage: account.leverage,
      balance: account.starting_balance,
      config,
    }
    console.log(paylog)
    const res = await fetch(`${API_BASE}/account/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: account.name,
        leverage: account.leverage,
        balance: account.starting_balance,
        config,
      }),
    });
    if (res.ok) {
      const data = await res.json();
      const accountId = data.account._id;  // ← updated to match new return format
      console.log('Account created with ID:', accountId);
      
      toast.success('Account created with Id!', accountId);
      // router.push(`/account/${accountId}`);
    } else {
      const err = await res.json();
      toast.error(`Failed: ${err.detail}`);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Create New Trading Account</h1>
            {/* Optional: Copy config from existing */}
            <div className="flex flex-col">
        <label className="text-sm mb-1">Copy Config From</label>
        <select
          value={copyFromId ?? ''}
          onChange={(e) => {
            const selectedId = e.target.value;
            setCopyFromId(selectedId);
            handleCopyConfig(selectedId);
          }}
          className="border px-2 py-1 rounded bg-black text-white"
        >
          <option value="">-- None --</option>
          {accounts.map((acc) => (
            <option key={acc._id} value={acc._id}>
              {acc.name}
            </option>
          ))}
        </select>
      </div>
      <div className="flex flex-col">
        <label className="text-sm">Starting Balance</label>
        <input
          type="number"
          value={account.starting_balance}
          onChange={(e) =>
            setAccount((prev) => ({
              ...prev,
              starting_balance: parseFloat(e.target.value),
            }))
          }
          className="border px-2 py-1 rounded"
        />
      </div>
      <TokenConfigEditor
        config={config}
        onChange={setConfig}
        account={account}
        onAccountChange={(updates) => setAccount((prev) => ({ ...prev, ...updates }))}
      />

      <div className="flex gap-4 pt-4">
        <Button onClick={handleSubmit}>Create Account</Button>
        <Button variant="outline" onClick={() => router.back()}>
          Cancel
        </Button>
      </div>
    </div>
  );
}
