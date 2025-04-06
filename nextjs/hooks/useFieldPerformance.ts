// hooks/useFieldPerformance.ts
import { useSelector } from 'react-redux';
import { RootState } from '@/store/store';
import { useMemo } from 'react';

export function useFieldPerformance(token: string, selectedField: string) {
  const trades = useSelector((state: RootState) =>
    Object.values(state.trades.byId).filter((t) => t.token === token)
  );
  const accountsById = useSelector((state: RootState) => state.accounts.byId);

  return useMemo(() => {
    const groups: Record<string, { count: number; totalPnL: number }> = {};

    for (const trade of trades) {
      const accountIdKey = (trade.account_ref || trade.account_id)?.toString?.();
      const account = accountsById[accountIdKey];
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

    const sorted = Object.entries(groups)
      .map(([value, stats]) => ({
        value,
        avgPnL: stats.totalPnL / stats.count,
        count: stats.count,
      }))
      .sort((a, b) => b.avgPnL - a.avgPnL);

    return sorted[0] || null; // top performing
  }, [trades, accountsById, selectedField, token]);
}
