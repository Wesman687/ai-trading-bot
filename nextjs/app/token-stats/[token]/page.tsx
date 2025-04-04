'use client';

import ComboInsightsModal from '@/components/TokenStats/ComboInsightsModal';
import TokenConfigBreakdown from '@/components/TokenStats/TokenConfigBreakdown';
import TokenStatsAccordion from '@/components/TokenStats/TokenStatsAccordion';
import TokenStatsChart from '@/components/TokenStats/TokenStatsChart';
import TokenStatsSummary from '@/components/TokenStats/TokenStatsSummary';
import TokenStrategyInsights from '@/components/TokenStats/TokenStrategyInsights';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useParams } from 'next/navigation';
import { useState } from 'react';

export default function TokenStats() {
    const { token } = useParams() as { token: string };
    const [selectedField, setSelectedField] = useState<FieldOptionValue>('stop_loss_pct');
    type FieldOptionValue = typeof fieldOptions[number]['value'];
    const [showCombo, setShowCombo] = useState(false);
    const fieldOptions = [
      { value: "stop_loss_pct", label: "Stop Loss %" },
      { value: "trailing_stop_pct", label: "Trailing Stop %" },
      { value: "volume_surge_min", label: "Volume Surge Min" },
      { value: "confidence_thresholds.1m", label: "Confidence (1m)" },
      { value: "confidence_thresholds.15m", label: "Confidence (15m)" },
      { value: "filters.macd_long.rsi_min", label: "MACD Long RSI Min" },
      { value: "filters.macd_long.macd_hist_min", label: "MACD Hist Min" },
      {
        value: "filters.macd_long.macd_direction_min",
        label: "MACD Direction Min",
      },
      {
        value: "filters.macd_long.volume_surge_min",
        label: "MACD Volume Surge Min",
      },
      { value: "filters.short_setup.rsi_max", label: "Short Setup RSI Max" },
      {
        value: "filters.short_setup.macd_hist_max",
        label: "Short Setup MACD Hist Max",
      },
      { value: "filters.short_setup.ema_20_buffer", label: "EMA 20 Buffer" },
      { value: "filters.short_setup.sma_20_buffer", label: "SMA 20 Buffer" },
      { value: "filters.short_setup.momentum_min", label: "Momentum Min" },
      {
        value: "filters.short_setup.min_bearish_count",
        label: "Min Bearish Count",
      },
      { value: "filters.base.doji_threshold.1m", label: "Doji Threshold (1m)" },
        { value: "filters.base.doji_threshold.15m", label: "Doji Threshold (15m)" },
        { value: "filters.base.doji_threshold.1h", label: "Doji Threshold (1h)" },
        { value: "filters.base.noise_ratio_max", label: "Noise Ratio Max" },
        { value: "filters.base.min_trend.1m", label: "Min Trend (1m)" },
        { value: "filters.base.min_trend.15m", label: "Min Trend (15m)" },
        { value: "filters.base.min_trend.1h", label: "Min Trend (1h)" },
    ] as const;
    return (
        <div className="p-4 space-y-6">
            <h1 className="text-2xl font-bold">{token.toUpperCase()} Strategy Overview</h1>

            <TokenStatsSummary token={token} />


            <TokenStatsChart token={token} />
            <div className="space-y-4">
                <div className="flex items-center gap-4">
                    <label htmlFor="field" className="text-sm font-medium">
                        View Config Performance By:
                    </label>
                    <Select
                        value={selectedField}
                        onValueChange={(value) => setSelectedField(value as FieldOptionValue)}
                    >
                        <SelectTrigger className='cursor-pointer'>
                            <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                            {fieldOptions.map((option) => (
                                <SelectItem key={option.value} value={option.value}>
                                    {option.label}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                    <Button className='cursor-pointer' onClick={() => setShowCombo(true)}>🔬 Custom Combo</Button>
                </div>

                <TokenStrategyInsights token={token} selectedField={selectedField} />
            </div>
            <TokenConfigBreakdown token={token} />
            {showCombo && <ComboInsightsModal token={token} onClose={() => setShowCombo(false)} />}

            <TokenStatsAccordion token={token} />
        </div>
    );
}
