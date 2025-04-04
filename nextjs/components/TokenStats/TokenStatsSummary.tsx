import { useSelector } from 'react-redux';
import { RootState } from '@/store/store';
import { Trade } from '@/types/account';
import { Card, CardContent } from '@/components/ui/card';

export default function TokenStatsSummary({ token }: { token: string }) {
  const trades = useSelector((state: RootState) =>
    Object.values(state.trades.byId).filter((t: Trade) => t.token === token)
  );

  const totalPnL = trades.reduce((acc, trade) => acc + (trade.pnl || 0), 0);
  const wins = trades.filter(t => t.pnl >= 0).length;
  const losses = trades.filter(t => t.pnl < 0).length;

  return (
    <Card>
      <CardContent className="grid grid-cols-3 gap-4">
        <div>
          <p className="text-sm text-muted-foreground">Total Trades</p>
          <p className="text-lg font-bold">{trades.length}</p>
        </div>
        <div>
          <p className="text-sm text-muted-foreground">Wins</p>
          <p className="text-lg font-bold text-green-600">{wins}</p>
        </div>
        <div>
          <p className="text-sm text-muted-foreground">Losses</p>
          <p className="text-lg font-bold text-red-600">{losses}</p>
        </div>
        <div>
          <p className="text-sm text-muted-foreground">Total PnL</p>
          <p className={`text-lg font-bold ${totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            ${totalPnL.toFixed(2)}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}