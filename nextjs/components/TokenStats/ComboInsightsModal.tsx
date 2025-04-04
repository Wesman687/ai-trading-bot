'use client';

import { useSelector } from 'react-redux';
import { RootState } from '@/store/store';
import { useMemo, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { MultiSelect } from '@/components/ui/multiselect';

export default function ComboInsightsModal({ token, onClose }: { token: string; onClose: () => void }) {
  const trades = useSelector((state: RootState) =>
    Object.values(state.trades.byId).filter((t) => t.token === token)
  );
  const accountsById = useSelector((state: RootState) => state.accounts.byId);

  const [fields, setFields] = useState<string[]>([]);

  const comboStats = useMemo(() => {
    const groups: Record<string, { count: number; totalPnL: number }> = {};

    for (const trade of trades) {
      const account = accountsById[trade.account_id];
      const config = account?.config?.[token];
      if (!config || fields.length === 0) continue;

      const values = fields.map((field) => {
        return field
          .split('.')
          .reduce((acc, part) => (acc && typeof acc === 'object' && part in acc ? acc[part] : undefined), config);
      });

      const key = values.join('|');
      if (!key.includes('undefined')) {
        if (!groups[key]) {
          groups[key] = { count: 0, totalPnL: 0 };
        }
        groups[key].count++;
        groups[key].totalPnL += trade.pnl || 0;
      }
    }

    return Object.entries(groups)
      .map(([key, stats]) => ({
        config: key,
        avgPnL: stats.totalPnL / stats.count,
        tradeCount: stats.count,
      }))
      .sort((a, b) => b.avgPnL - a.avgPnL);
  }, [trades, accountsById, fields, token]);

  const allFields = [
    'exit_strategy.stop_loss_pct',
    'exit_strategy.trailing_stop_pct',
    'exit_strategy.volume_surge_min',
    'confidence_thresholds.1m',
    'confidence_thresholds.15m',
    'filters.macd_long.rsi_min',
    'filters.macd_long.macd_hist_min',
    'filters.macd_long.macd_direction_min',
    'filters.macd_long.volume_surge_min',
    'filters.short_setup.rsi_max',
    'filters.short_setup.macd_hist_max',
    'filters.short_setup.ema_20_buffer',
    'filters.short_setup.sma_20_buffer',
    'filters.short_setup.momentum_min',
    'filters.short_setup.min_bearish_count',
  ];

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>Custom Config Combo Insights</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <MultiSelect
            label="Choose Config Fields"
            options={allFields.map((f) => ({ label: f, value: f }))}
            value={fields}
            onChange={setFields}
          />

          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={comboStats}>
              <XAxis dataKey="config" hide />
              <YAxis />
              <Tooltip
                formatter={(val: number, name: string) =>
                  name === 'avgPnL' ? [`$${val.toFixed(2)}`, 'Avg PnL'] : [val, 'Trades']
                }
              />
              <Bar dataKey="avgPnL" fill="#4f46e5" />
            </BarChart>
          </ResponsiveContainer>

          <ul className="text-sm space-y-1 max-h-60 overflow-y-auto">
            {comboStats.map((s, i) => (
              <li key={i}>
                <strong>{s.config}</strong> → Avg PnL: ${s.avgPnL.toFixed(2)} ({s.tradeCount} trades)
              </li>
            ))}
          </ul>

          <div className="text-right">
            <Button onClick={onClose}>Close</Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
