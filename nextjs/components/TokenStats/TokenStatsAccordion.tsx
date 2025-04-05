import {  useMemo, useState } from 'react';
import { useSelector } from 'react-redux';
import { RootState } from '@/store/store';
import { Trade } from '@/types/account';
import { format } from 'date-fns';
import { Card, CardContent } from '@/components/ui/card';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export default function TokenStatsAccordion({ token }: { token: string }) {
  const trades = useSelector((state: RootState) =>
    Object.values(state.trades.byId).filter((t: Trade) => t.token === token)
  );
  const accountsById = useSelector((state: RootState) => state.accounts.byId);

  const [sortOrder, setSortOrder] = useState<'top' | 'worst' | 'recent'>('recent');

  const groupedByDate = useMemo(() => {
    const grouped: Record<string, Trade[]> = {};
    for (const trade of trades) {
      const dateKey = format(new Date(trade.entry_time), 'yyyy-MM-dd');
      if (!grouped[dateKey]) grouped[dateKey] = [];
      grouped[dateKey].push(trade);
    }
    return grouped;
  }, [trades]);

  const sortedDates = useMemo(() => {
    return Object.keys(groupedByDate).sort((a, b) => {
      const aTrades = groupedByDate[a];
      const bTrades = groupedByDate[b];
      const aTotal = aTrades.reduce((acc, t) => acc + (t.pnl || 0), 0);
      const bTotal = bTrades.reduce((acc, t) => acc + (t.pnl || 0), 0);
      if (sortOrder === 'top') return bTotal - aTotal;
      if (sortOrder === 'worst') return aTotal - bTotal;
      return new Date(b).getTime() - new Date(a).getTime();
    });
  }, [groupedByDate, sortOrder]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Trade Logs</h2>
        <Select value={sortOrder} onValueChange={(value) => setSortOrder(value as 'top' | 'worst' | 'recent')}>
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="Sort by" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="recent">Most Recent</SelectItem>
            <SelectItem value="top">Top PnL</SelectItem>
            <SelectItem value="worst">Worst PnL</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Accordion type="single" collapsible>
        {sortedDates.map((date) => (
          <AccordionItem key={date} value={date}>
            <AccordionTrigger>
              {date} — {groupedByDate[date].length} trades
            </AccordionTrigger>
            <AccordionContent>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                {groupedByDate[date].map((trade, index) => {
                  const accountConfig = accountsById[trade.account_id || trade.account_ref]?.config?.[trade.token];
                  return (
                    <Card key={index} className="p-2 text-sm">
                      <CardContent className="space-y-1">
                        <p className="font-semibold">{trade.direction.toUpperCase()}</p>
                        <p>Entry: ${trade.entry_price}</p>
                        <p>Exit: ${trade.exit_price}</p>
                        <p className={trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'}>
                          PnL: ${trade.pnl?.toFixed(2)}
                        </p>
                        <p className="text-xs text-muted-foreground">Account: {trade.account_id || trade.account_ref}</p>
                        {accountConfig && (
                          <pre className="text-xs bg-gray-800 text-white p-2 rounded overflow-x-auto">
                            {JSON.stringify(accountConfig.exit_strategy, null, 2)}
                          </pre>
                        )}
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </div>
  );
}