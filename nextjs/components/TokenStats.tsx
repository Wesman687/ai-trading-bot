'use client';

import { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '@/store/store';
import { Trade } from '@/types/account';
import { Card, CardContent } from '@/components/ui/card';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { format } from 'date-fns';

export default function TokenStats({ token }: { token: string }) {
  const trades = useSelector((state: RootState) =>
    Object.values(state.trades.byId).filter((t: Trade) => t.token === token)
  );

  const [groupedByDate, setGroupedByDate] = useState<Record<string, Trade[]>>({});

  useEffect(() => {
    const grouped: Record<string, Trade[]> = {};
    for (const trade of trades) {
      const dateKey = format(new Date(trade.entry_time), 'yyyy-MM-dd');
      if (!grouped[dateKey]) grouped[dateKey] = [];
      grouped[dateKey].push(trade);
    }
    setGroupedByDate(grouped);
  }, [trades]);

  const totalPnL = trades.reduce((acc, trade) => acc + (trade.pnl || 0), 0);
  const wins = trades.filter(t => t.pnl >= 0).length;
  const losses = trades.filter(t => t.pnl < 0).length;

  return (
    <div className="p-4 space-y-6">
      <h1 className="text-2xl font-bold">{token.toUpperCase()} Strategy Overview</h1>

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

      <Accordion type="single" collapsible>
        {Object.entries(groupedByDate).map(([date, dayTrades]) => (
          <AccordionItem key={date} value={date}>
            <AccordionTrigger>
              {date} — {dayTrades.length} trades
            </AccordionTrigger>
            <AccordionContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                {dayTrades.map((trade, index) => (
                  <Card key={index} className="p-2 text-sm">
                    <CardContent className="space-y-1">
                      <p className="font-semibold">{trade.direction.toUpperCase()}</p>
                      <p>Entry: ${trade.entry_price}</p>
                      <p>Exit: ${trade.exit_price}</p>
                      <p className={trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'}>
                        PnL: ${trade.pnl?.toFixed(2)}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Account: {trade.account_id}
                      </p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </div>
  );
}