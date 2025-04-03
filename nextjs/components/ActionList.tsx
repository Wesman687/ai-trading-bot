'use client';
import { useSelector } from 'react-redux';
import { RootState } from '@/store/store';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { useState } from 'react';
import { Button } from '@/components/ui/button';

export default function AccountList() {
  const accounts = useSelector((state: RootState) => state.accounts.allIds.map(id => state.accounts.byId[id]));
  const [sortBy, setSortBy] = useState<'pnl' | 'losses' | 'wins' | 'trades'>('pnl');

  const sortedAccounts = [...accounts].sort((a, b) => {
    if (sortBy === 'pnl') return b.net_pnl - a.net_pnl;
    if (sortBy === 'losses') return (b.loss_count || 0) - (a.loss_count || 0);
    if (sortBy === 'wins') return (b.win_count || 0) - (a.win_count || 0);
    if (sortBy === 'trades') return (b.closed_trade_ids?.length || 0) - (a.closed_trade_ids?.length || 0);
    return 0;
  });

  const renderAccountCard = (account: typeof accounts[number]) => {
    const winCount = account.win_count || 0;
    const lossCount = account.loss_count || 0;
    const total = winCount + lossCount;
    const winRate = total > 0 ? (winCount / total * 100).toFixed(1) : 'N/A';
    const netPnlClass = account.net_pnl >= 0 ? 'text-green-600' : 'text-red-600';
    const balanceClass = account.balance >= account.starting_balance ? 'text-green-600' : 'text-red-600';
    const winRateClass = winRate !== 'N/A' && parseFloat(winRate) >= 50 ? 'text-green-600' : 'text-red-600';

    return (
      <Link key={account.account_id} href={`/account/${account.account_id}`}>
        <Card className="cursor-pointer hover:shadow-xl transition">
          <CardContent>
            <h2 className="text-lg font-semibold">{account.name}</h2>
            <p className="text-sm text-gray-500">
              Available Balance: ${account.available_balance.toFixed(2)}
            </p>
            <div className="flex w-full justify-between">
              <p className={`text-sm ${balanceClass}`}>
                Balance: ${account.balance.toFixed(2)}
              </p>
              <p className={`text-sm ${netPnlClass}`}>
                Net PnL: ${account.net_pnl.toFixed(2)}
              </p>
            </div>
            <div className="flex w-full justify-between">
              <p className={`text-sm ${winRateClass}`}>
                Win Rate: {winRate}%
              </p>
              <p className="text-sm">
                Trades: {account.closed_trade_ids?.length || 0}
              </p>
            </div>
            <div className="flex w-full justify-between">
              <p>Open Trades: {account.open_trade_ids?.length || 0}</p>
              <p>wins: {account.win_count || 0}</p>
              <p>losses: {account.loss_count || 0}</p>
            </div>
          </CardContent>
        </Card>
      </Link>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex gap-4 mb-4 flex-wrap">
        <Button variant={sortBy === 'pnl' ? 'default' : 'outline'} onClick={() => setSortBy('pnl')}>Top PnL</Button>
        <Button variant={sortBy === 'losses' ? 'default' : 'outline'} onClick={() => setSortBy('losses')}>Most Losses</Button>
        <Button variant={sortBy === 'wins' ? 'default' : 'outline'} onClick={() => setSortBy('wins')}>Most Wins</Button>
        <Button variant={sortBy === 'trades' ? 'default' : 'outline'} onClick={() => setSortBy('trades')}>Most Trades</Button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {sortedAccounts.map(renderAccountCard)}
      </div>
    </div>
  );
}
