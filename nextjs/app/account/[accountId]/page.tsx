// app/(routes)/account/[id]/page.tsx
'use client';

import { use, useEffect, useMemo, useState } from 'react';
import {
  Card,
  CardContent,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useDispatch, useSelector } from 'react-redux';
import { deleteAccount, fetchAccountById } from '@/actions/accounts';
import { useRouter } from 'next/navigation';
import { Trade } from '@/types/account';
import { Line, LineChart, Tooltip, XAxis, YAxis } from 'recharts';
import TradeHistoryCard from '@/components/TradeHistoryCard';
import { selectTradeLogForAccount } from '@/store/selectors/trade';
import { selectAccountById } from '@/store/selectors/account';


export default function AccountPage({ params }: { params: Promise<{ accountId: string }> }) {
  const { accountId } = use(params); // ✅ unwrap the promise

  const memoizedSelector = useMemo(() => selectAccountById(accountId), [accountId]);
  const account = useSelector(memoizedSelector);
    const dispatch = useDispatch();
    const [showConfig, setShowConfig] = useState(false);
    const memoizedTradeLogSelector = useMemo(() => selectTradeLogForAccount(accountId), [accountId]);
    const tradeLog = useSelector(memoizedTradeLogSelector);
    const router = useRouter()
    useEffect(() => {
      if (!account) {
        fetchAccountById(accountId)(dispatch);
      } 
    }, [accountId, dispatch, account]);
  
    if (!account) return <div className="text-center mt-10">Loading account...</div>;
  
    const { balance, net_pnl, open_trades, config } = account;

    console.log(account)
    return (
      <div className="p-6 space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Account: {accountId}</h1>
          <div className="space-x-2">
            <Button onClick={() => router.push(`/account/${accountId}/config`)}>
              Edit Config
            </Button>
            <Button
              variant="destructive"
              onClick={() => deleteAccount(accountId)}
            >
              Delete
            </Button>
          </div>
        </div>

        <Card>
          <CardContent className="grid grid-cols-2 md:grid-cols-4 gap-4 align-center">
            <div>
              <p className="text-sm text-gray-200">Balance</p>
              <p className="text-lg font-bold">${balance.toFixed(2)}</p>
            </div>

            <div>
              <p className="text-sm text-gray-200">Available Balance</p>
              <p
                className={`text-lg font-bold ${
                  account.available_balance > 0
                    ? "text-green-600"
                    : net_pnl < 0
                    ? "text-red-600"
                    : "text-gray-600"
                }`}
              >
                ${account.available_balance.toFixed(2)}
              </p>
            </div>

            <div>
              <p className="text-sm text-gray-200">Trading Risk</p>
              <p className="text-lg font-bold">{account.trade_risk_pct}x</p>
            </div>

            <div>
              <p className="text-sm text-gray-200">Net PnL</p>
              <p
                className={`text-lg font-bold ${
                  net_pnl > 0
                    ? "text-green-600"
                    : net_pnl < 0
                    ? "text-red-600"
                    : "text-gray-600"
                }`}
              >
                ${net_pnl.toFixed(2)}
              </p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <h2 className="text-xl font-semibold mb-4">Open Trades</h2>
            {open_trades.length === 0 ? (
              <p>No open trades.</p>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 max-h-[30vh] overflow-y-auto pr-2">
                {open_trades.map((trade: Trade) => (
                  <div
                    key={trade.trade_id}
                    className="bg-muted p-3 rounded-lg shadow-sm border"
                  >
                    <div className="flex justify-between font-semibold">
                      <span>{trade.token.toUpperCase()}</span>
                      <span
                        className={
                          trade.current_pnl >= 0
                            ? "text-green-600"
                            : "text-red-600"
                        }
                      >
                        {trade.current_pnl >= 0 ? "+" : ""}$
                        {trade.current_pnl.toFixed(2)}
                      </span>
                    </div>
                    <div className="text-sm text-gray-200">
                      {trade.direction.toUpperCase()} — Entry: $
                      {trade.entry_price} — Size: ${trade.trade_size.toFixed(4)}
                    </div>
                    <div
                      className={`text-xs mt-1 ${
                        trade.current_price > trade.entry_price
                          ? "text-green-600"
                          : trade.current_price < trade.entry_price
                          ? "text-red-600"
                          : "text-gray-500"
                      }`}
                    >
                      Current Price: ${trade.current_price}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {tradeLog?.length > 9 && <TradeHistoryCard trades={tradeLog} />}
        <Card>
          <CardContent>
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold mb-4">Config</h2>
              <Button
                onClick={() => setShowConfig(!showConfig)}
                variant="outline"
              >
                {showConfig ? "Hide" : "Show"}
              </Button>
            </div>
            {showConfig && (
              <pre className="bg-gray-900 text-white text-sm p-4 rounded-xl overflow-x-auto">
                {JSON.stringify(config, null, 2)}
              </pre>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <h2 className="text-xl font-semibold mb-4">Performance Chart</h2>
            <LineChart
              width={500}
              height={300}
              data={account.performance || []}
            >
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="net_pnl"
                stroke="#8884d8"
                strokeWidth={2}
              />
            </LineChart>
          </CardContent>
        </Card>
      </div>
    );
  }

