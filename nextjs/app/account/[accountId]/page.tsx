// app/(routes)/account/[id]/page.tsx
'use client';

import { useEffect } from 'react';
import {
  Card,
  CardContent,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RootState } from '@/store/store';
import { useDispatch, useSelector } from 'react-redux';
import { deleteAccount, fetchAccountById } from '@/actions/accounts';
import { useRouter } from 'next/navigation';
import { Trade } from '@/types/account';
import { Line, LineChart, Tooltip, XAxis, YAxis } from 'recharts';


export default function AccountPage({ params }: { params: { accountId: string } }) {
    const accountId = params.accountId;
    const account = useSelector((state: RootState) => state.accounts.byId[accountId]);
    const dispatch = useDispatch();
    const router = useRouter()
    
    useEffect(() => {
      if (!account) {
        fetchAccountById(accountId)(dispatch);
      }
    }, [accountId, dispatch, account]);
  
    if (!account) return <div className="text-center mt-10">Loading account...</div>;
  
    const { balance, net_pnl, open_trades, trade_log, config } = account;
  
    return (
      <div className="p-6 space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Account: {accountId}</h1>
          <div className="space-x-2">
          <Button onClick={() => router.push(`/account/${accountId}/config`)}>Edit Config</Button>
            <Button variant="destructive" onClick={() => deleteAccount(accountId)}>Delete</Button>
          </div>
        </div>
  
        <Card>
          <CardContent className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-lg">Balance:</p>
              <p className="text-xl font-semibold">${balance.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-lg">Net PnL:</p>
              <p className="text-xl font-semibold">${net_pnl.toFixed(2)}</p>
            </div>
          </CardContent>
        </Card>
  
        <Card>
          <CardContent>
            <h2 className="text-xl font-semibold mb-4">Open Trades</h2>
            {open_trades.length === 0 ? (
              <p>No open trades.</p>
            ) : (
              <ul className="list-disc pl-4 space-y-2">
                {open_trades.map((trade: Trade) => (
                  <li key={trade.trade_id}>
                    {trade.token} - {trade.direction} - Entry: ${trade.entry_price} - Size: ${trade.trade_size}
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
  
        <Card>
          <CardContent>
            <h2 className="text-xl font-semibold mb-4">Trade History</h2>
            {trade_log.length === 0 ? (
              <p>No trades yet.</p>
            ) : (
              <ul className="list-disc pl-4 space-y-2">
                {trade_log.map((trade: Trade, index: number) => (
                  <li key={index}>
                    {trade.token} - {trade.direction} - Entry: ${trade.entry_price} → Exit: ${trade.exit_price} = {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
  
        <Card>
          <CardContent>
            <h2 className="text-xl font-semibold mb-4">Config</h2>
            <pre className="bg-gray-900 text-white text-sm p-4 rounded-xl overflow-x-auto">
              {JSON.stringify(config, null, 2)}
            </pre>
          </CardContent>
        </Card>
  
        <Card>
          <CardContent>
            <h2 className="text-xl font-semibold mb-4">Performance Chart</h2>
            <LineChart width={500} height={300} data={account.performance || []}>
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="net_pnl" stroke="#8884d8" strokeWidth={2} />
            </LineChart>
          </CardContent>
        </Card>
      </div>
    );
  }

