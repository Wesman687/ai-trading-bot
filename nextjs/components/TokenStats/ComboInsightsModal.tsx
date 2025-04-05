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
      const accountIdKey = (trade.account_ref || trade.account_id)?.toString?.();
      const account = accountsById[accountIdKey];
      const config = account?.config?.[token];
      if (!config || fields.length === 0) continue;

      interface ConfigValueObject {
        [key: string]: string | number | undefined | ConfigValueObject;
      }
      type ConfigValue = string | number | undefined | ConfigValueObject;
      
      const values = fields.map((field) => {
              return field.split('.').reduce((acc: ConfigValue, part) => {
                if (acc && typeof acc === 'object' && part in acc) {
                  return acc[part];
                }
                return undefined;
              }, config as unknown as ConfigValue);
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
    'filters.base.doji_threshold.1m',
    'filters.base.doji_threshold.15m',
    'filters.base.doji_threshold.1h',
    'filters.base.noise_ratio_max',
    'filters.base.min_trend.1m',
    'filters.base.min_trend.15m',
    'filters.base.min_trend.1h',
  ];


  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent
        className="w-[95vw] max-w-[1300px] sm:rounded-lg p-6"
        style={{ width: "95vw", maxWidth: "1300px" }}
      >
        <DialogHeader>
          <DialogTitle>Custom Config Combo Insights</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 w-full flex flex-col gap-4">
          <div className="flex gap-5 items-center">
            <div className="w-max">Choose Config Fields</div>
            <MultiSelect
              options={allFields.map((f) => ({ label: f, value: f }))}
              selected={fields}
              onChange={setFields}
            />
          </div>
          {fields.length > 0 && (
            <div className="text-sm text-muted-foreground mt-2 w-full">
              <span className="font-medium">Selected Fields:</span>{" "}
              {fields.join(" | ")}
            </div>
          )}
          <div className="w-full">
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={comboStats}>
                <XAxis dataKey="config" hide />
                <YAxis />
                <Tooltip
                  formatter={(val: number, name: string) =>
                    name === "avgPnL"
                      ? [`$${val.toFixed(2)}`, "Avg PnL"]
                      : [val.toFixed(2), "Trades"]
                  }
                />
                <Bar dataKey="avgPnL" fill="#4f46e5" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <ul className="text-sm space-y-1 w-full max-h-60 overflow-y-auto">
            {comboStats.map((s, i) => (
              <li key={i}>
                <strong>{s.config}</strong> → Avg PnL: ${s.avgPnL.toFixed(2)} (
                {s.tradeCount} trades)
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
