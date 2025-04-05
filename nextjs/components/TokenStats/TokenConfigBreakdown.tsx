import { useSelector } from 'react-redux';
import { RootState } from '@/store/store';
import { Trade } from '@/types/account';
import { Card, CardContent } from '@/components/ui/card';

export default function TokenConfigBreakdown({ token }: { token: string }) {
  const accounts = useSelector((state: RootState) => state.accounts.byId);
  const trades = useSelector((state: RootState) =>
    Object.values(state.trades.byId).filter((t: Trade) => t.token === token && t.account_id || t.account_ref)
  );

  const configMap: Record<string, { count: number; totalPnL: number }> = {};

  trades.forEach((trade) => {
    const config = JSON.stringify(accounts[trade.account_id]?.config?.[token]?.exit_strategy);
    if (config) {
      if (!configMap[config]) {
        configMap[config] = { count: 0, totalPnL: 0 };
      }
      configMap[config].count++;
      configMap[config].totalPnL += trade.pnl || 0;
    }
  });

  return (
    <Card>
      <CardContent>
        <h2 className="text-lg font-semibold mb-4">Strategy Config Performance</h2>
        <div className="space-y-4 max-h-[40vh] overflow-y-auto pr-2">
          {Object.entries(configMap).map(([config, stats], idx) => (
            <div key={idx} className="p-2 border rounded bg-muted text-sm">
              <p className="text-muted-foreground mb-1">Trades: {stats.count}</p>
              <p className={stats.totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}>
                PnL: ${stats.totalPnL.toFixed(2)}
              </p>
              <pre className="bg-gray-800 text-white text-xs p-2 rounded mt-2 overflow-x-auto">
                {JSON.stringify(JSON.parse(config), null, 2)}
              </pre>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}