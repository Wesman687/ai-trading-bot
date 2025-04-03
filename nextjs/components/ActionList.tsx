'use client';
import { useSelector } from 'react-redux';
import { RootState } from '@/store/store';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { Account } from '@/types/account';
export default function AccountList() {
    const allAccounts = useSelector((state: RootState) => state.accounts.allIds.map(id => state.accounts.byId[id]));

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {allAccounts.map((account: Account) => (
        <Link key={account.account_id} href={`/account/${account.account_id}`}>
          <Card className="cursor-pointer hover:shadow-xl transition">
            <CardContent>
              <h2 className="text-lg font-semibold">{account.name}</h2>
              <div className="flex w-full justify-between">
                <p>Balance: ${account.balance.toFixed(2)}</p>
                <p>Net PnL: ${account.net_pnl.toFixed(2)}</p>
              </div>
              <div className="flex w-full justify-between">
                <p>Win Count: {account.win_count}</p>
                <p>Loss Count: {account.loss_count}</p>
              </div>
              <div className="flex w-full justify-between">
                <p>Open Trades: {account.open_trade_ids.length}</p>
                <p>Trade Log: {account.trade_log.length}</p>
              </div>
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  );
}
