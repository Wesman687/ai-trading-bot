'use client'
import {   useEffect, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { AppDispatch } from '@/store/store';
import { Button } from '@/components/ui/button';
import {  updateAccountConfig } from '@/actions/accounts';
import { TokenConfig } from '@/types/config';
import TokenConfigEditor from '@/components/TokenConfigEditor';
import { useRouter } from 'next/navigation';
import { selectAccountById } from '@/store/selectors/account';

export interface AccountConfig {
  [token: string]: TokenConfig;
}
export default function AccountConfigClient({ accountId }: { accountId: string }) {
    const router = useRouter();
    const dispatch = useDispatch<AppDispatch>();
    const memoizedSelector = useMemo(() => selectAccountById(accountId), [accountId]);
    const account = useSelector(memoizedSelector);
    const [localConfig, setLocalConfig] = useState<AccountConfig | null>(null);
    const [generalFields, setGeneralFields] = useState({
      name: account.name,
      leverage: account.leverage,
      trade_risk_pct: account.trade_risk_pct,
      trade_size: account.trade_size,
    });
    const handleGeneralChange = (updates: Partial<typeof generalFields>) => {
      setGeneralFields(prev => ({ ...prev, ...updates }));
    };
    useEffect(() => {
      if (account && !localConfig) {
        setLocalConfig(JSON.parse(JSON.stringify(account.config))); // deep copy to prevent mutation
      }
    }, [account, localConfig]);

    if (!account || !localConfig) return <div className="p-6">Loading account...</div>;

    const handleSave = () => {
      dispatch(updateAccountConfig(account.account_id, {
        config: localConfig,
        ...generalFields,
      }));
    };
    
  const handleCancel = () => {
    router.push(`/account/${accountId}`);
  };
  

  return (
    <div className="p-6 space-y-6">
      <TokenConfigEditor config={localConfig} onChange={setLocalConfig} onAccountChange={handleGeneralChange} account={generalFields} />
      <div className="flex justify-end gap-4">
        <Button variant="outline" onClick={handleCancel}>Cancel</Button>
        <Button onClick={handleSave}>Save</Button>
      </div>
    </div>
  );
}

