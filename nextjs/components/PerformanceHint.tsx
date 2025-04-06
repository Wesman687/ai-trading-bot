'use client';

import { usePerformanceInsights } from '@/hooks/usePerformanceInsights';
import { Button } from './ui/button';

type Props = {
  token: string;
  fieldPath: string; // dot notation like 'filters.macd_long.rsi_min'
  onApply: (value: number) => void;
  className?: string;
};

export default function PerformanceHint({ token, fieldPath, onApply, className }: Props) {
  const insight = usePerformanceInsights(token, fieldPath);

  if (!insight) return null;

  return (
    <span className={`text-xs text-muted-foreground flex items-center gap-1 ${className}`}>
      Best: {insight.value} (${insight.avgPnL.toFixed(2)})
      <Button
        variant="link"
        className="px-1 py-0 h-auto text-blue-600 text-xs cursor-pointer"
        onClick={() => onApply(parseFloat(insight.value))}
      >
        Apply
      </Button>
    </span>
  );
}
