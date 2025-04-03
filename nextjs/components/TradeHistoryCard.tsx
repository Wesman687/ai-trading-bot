import { Trade } from '@/types/account';
import { Card, CardContent } from '@/components/ui/card';

type Props = {
  trades: Trade[];
};

export default function TradeHistoryCard({ trades }: Props) {
  const totalTrades = trades.length;
  const totalPnL = trades.reduce((acc, trade) => acc + trade.pnl, 0);
  const winCount = trades.filter((t) => t.pnl > 0).length;
  const lossCount = trades.filter((t) => t.pnl < 0).length;
  const winRate = totalTrades > 0 ? ((winCount / totalTrades) * 100).toFixed(1) : 'N/A';
  const totalPnLClass = totalPnL >= 0 ? 'text-green-600' : 'text-red-600';

  return (
    <Card>
      <CardContent>
        <h2 className="text-xl font-semibold mb-4">Trade History</h2>
        {trades.length === 0 ? (
          <p>No trades yet.</p>
        ) : (
          <>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 max-h-[30vh] overflow-y-auto">
              {trades.map((trade) => (
                <div
                  key={trade.trade_id}
                  className="bg-muted p-3 rounded-lg shadow-sm border"
                >
                  <div className="flex justify-between font-semibold">
                    <span>{trade.token.toUpperCase()}</span>
                    <span className={trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'}>
                      {trade.pnl >= 0 ? '+' : ''}
                      ${trade.pnl.toFixed(2)}
                    </span>
                  </div>
                  <div className="text-sm text-gray-200">
                    {trade.direction.toUpperCase()} — Entry: ${trade.entry_price} → Exit: ${trade.exit_price}
                  </div>
                  <div className="text-xs text-gray-200 mt-1">
                    Reason: {trade.reason}
                  </div>
                </div>
              ))}
            </div>

            {/* 📊 Summary */}
            <div className="mt-6 border-t pt-4 text-large text-gray-200">
              <div className='flex justify-evenly'>
              <p>Total Trades: <span className="font-semibold">{totalTrades}</span></p>
              <p>Wins: <span className="text-green-600 font-semibold">{winCount}</span> | Losses: <span className="text-red-600 font-semibold">{lossCount}</span></p>
              <p>Win Rate: <span className={winRate !== 'N/A' && parseFloat(winRate) >= 50 ? 'text-green-600' : 'text-red-600'}>{winRate}%</span></p>
              <p>Total PnL: <span className={`font-bold ${totalPnLClass}`}>${totalPnL.toFixed(2)}</span></p>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}