'use client';

import { useSelector } from 'react-redux';
import { RootState } from '@/store/store';
import { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

type Props = {
  token: string;
  selectedField: 'stop_loss_pct' | 'trailing_stop_pct' | 'volume_surge_min' | 'confidence_thresholds.1m' | 'confidence_thresholds.15m' | 
    'filters.macd_long.rsi_min' | 'filters.macd_long.macd_hist_min' | 'filters.macd_long.macd_direction_min' | 'filters.macd_long.volume_surge_min' |
     'filters.short_setup.rsi_max' | 'filters.short_setup.macd_hist_max' | 'filters.short_setup.ema_20_buffer' | 'filters.short_setup.sma_20_buffer' |
      'filters.short_setup.momentum_min' | 'filters.short_setup.min_bearish_count' | 'filters.base.doji_threshold.1m' | 'filters.base.doji_threshold.15m' |
       'filters.base.doji_threshold.1h' | 'filters.base.noise_ratio_max' | 'filters.base.min_trend.1m' | 'filters.base.min_trend.15m' | 'filters.base.min_trend.1h';
};

export default function TokenStrategyInsights({ token, selectedField }: Props) {
  const trades = useSelector((state: RootState) =>
    Object.values(state.trades.byId).filter((t) => t.token === token)
  );

  const accountsById = useSelector((state: RootState) => state.accounts.byId);

  const groupedStats = useMemo(() => {
    const groups: Record<string, { count: number; totalPnL: number }> = {};

    for (const trade of trades) {
      const accountIdKey = (trade.account_ref || trade.account_id)?.toString?.();
      const account = accountsById[accountIdKey]
        const config = account?.config?.[token];
        if (!config) continue;
      
        const strategyRoot = selectedField.includes('.') ? config : config.exit_strategy;
        if (!strategyRoot) continue;
      
        const getNestedValue = (obj: unknown, path: string): unknown => {
          return path.split('.').reduce((acc, part) => {
            if (acc && typeof acc === 'object' && part in acc) {
              return (acc as Record<string, unknown>)[part];
            }
            return undefined;
          }, obj);
        };
      
        const rawValue = getNestedValue(strategyRoot, selectedField);
        const key = rawValue?.toString();
        if (!key) continue;

      if (!groups[key]) {
        groups[key] = { count: 0, totalPnL: 0 };
      }

      groups[key].count += 1;
      groups[key].totalPnL += trade.pnl || 0;
    }

    return Object.entries(groups)
      .map(([value, stats]) => ({
        [selectedField]: value,
        avgPnL: stats.totalPnL / stats.count,
        tradeCount: stats.count,
      }))
      .sort((a, b) => b.avgPnL - a.avgPnL); // Sort best to worst
  }, [trades, accountsById, selectedField, token]);

  return (
    <div className="space-y-2">
      <h2 className="text-lg font-bold">Performance by {selectedField}</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={groupedStats}>
          <XAxis dataKey={selectedField} />
          <YAxis />
          <Tooltip
            formatter={(value: number, name: string) =>
              name === 'avgPnL'
                ? [`$${value.toFixed(2)}`, 'Avg PnL']
                : [value, 'Trades']
            }
            labelFormatter={(label) => `${selectedField}: ${label}`}
          />
          <Bar dataKey="avgPnL" fill="#8884d8" name="Avg PnL" />
        </BarChart>
      </ResponsiveContainer>
      <ul className="text-sm text-muted-foreground">
        {groupedStats.map((s) => (
          <li key={s[selectedField]}>
            {selectedField}: <strong>{s[selectedField]}</strong> — Avg PnL: ${s.avgPnL.toFixed(2)} ({s.tradeCount} trades)
          </li>
        ))}
      </ul>
    </div>
  );
}
