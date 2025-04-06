'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { toast } from 'sonner';
import { Button } from './ui/button';
import { Account } from '@/types/account';
import { Config } from '@/types/config';
import PerformanceHint from './PerformanceHint';

type Props = {
  config: Config;
  account: {
    name: string;
    leverage: number;
  };
  onChange: (config: Config) => void;
  onAccountChange: (updates: Partial<Account>) => void;
};

export default function TokenConfigEditor({ config, onChange, account, onAccountChange }: Props) {
  const [activeToken, setActiveToken] = useState<string>(Object.keys(config)[0]);
  const [liveConfig, setLiveConfig] = useState<Config>({});
  const [riskLevels, setRiskLevels] = useState<Record<string, number>>({});
  const [tempValues, setTempValues] = useState<Record<string, string>>({});
  const presets = [
    { "1m": 0.95, "15m": 0.92, "1h": 0.9, "1d": 0.88 },
    { "1m": 0.88, "15m": 0.85, "1h": 0.82, "1d": 0.8 },
    { "1m": 0.82, "15m": 0.78, "1h": 0.72, "1d": 0.67 },
    { "1m": 0.72, "15m": 0.68, "1h": 0.62, "1d": 0.57 },
    { "1m": 0.65, "15m": 0.6, "1h": 0.55, "1d": 0.5 }
  ];


  useEffect(() => {
    setLiveConfig(JSON.parse(JSON.stringify(config)));
    const levels: Record<string, number> = {};
    Object.keys(config).forEach((token) => (levels[token] = 2));
    setRiskLevels(levels);
  }, [config]);

  type InputValue = number | boolean | Record<string, string | number | boolean>;
  const handleInputChange = (path: string[], value: InputValue) => {
    if (!activeToken || !liveConfig) return;
  
    if (path.some((p) => p === undefined || p === null)) {
      console.warn("🚨 Skipping input due to bad path", path, value);
      return;
    }
  
    const updated = JSON.parse(JSON.stringify(liveConfig[activeToken]));
    let nested = updated;
    for (let i = 0; i < path.length - 1; i++) nested = nested[path[i]];
    nested[path[path.length - 1]] = value;
  
    const updatedConfig = { ...liveConfig, [activeToken]: updated };
    setLiveConfig(updatedConfig);
    onChange(updatedConfig);
  };

  const applyRiskPreset = (level: number) => {
    const newThresholds = presets[level];
    handleInputChange(['confidence_thresholds'], newThresholds);
    setRiskLevels(prev => ({ ...prev, [activeToken]: level }));
    toast.success(`${activeToken} preset level ${level + 1} applied`);
  };

  const tokenConfig = liveConfig[activeToken];
  if (!tokenConfig) return <div className="text-sm p-4">Loading token config...</div>;

  const renderNumberInput = (key: string, path: string[], value: number) => (
    <input
      type="text"
      value={tempValues[key] ?? value.toString()}
      onChange={(e) => {
        const raw = e.target.value;
        setTempValues((prev) => ({ ...prev, [key]: raw }));
        const parsed = parseFloat(raw);
        if (!isNaN(parsed)) {
          handleInputChange(path, parsed);
        }
      }}
      className="border text-sm px-2 py-1 rounded w-24 no-spinner"
    />
  );

  return (
    <div className="space-y-6">
      {/* Token Tabs */}
      <div className="flex gap-4 mb-4">
        {Object.keys(config).map((token) => (
          <Button
            key={token}
            variant={token === activeToken ? 'default' : 'outline'}
            onClick={() => setActiveToken(token)}
          >
            {token}
          </Button>
        ))}
      </div>

      {/* Risk Slider */}
      <div className="mb-4">
        <label className="font-medium">Risk Level Preset</label>
        <Slider
          min={0}
          max={4}
          step={1}
          value={[riskLevels[activeToken] ?? 2]}
          onValueChange={([val]) => applyRiskPreset(val)}
        />
      </div>

      {/* General Config */}
      <Card>
        <CardContent className="space-y-2">
          <h2 className="font-semibold text-lg">General</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col">
              <label className="text-sm">Account Name</label>
              <input
                type="text"
                value={account.name}
                onChange={(e) => onAccountChange({ name: e.target.value })}
                className="border px-2 py-1 rounded"
              />
            </div>
            <div className="flex flex-col">
              <label className="text-sm">Leverage</label>
              <input
                type="number"
                step="0.1"
                value={account.leverage}
                onChange={(e) => {
                  const value = parseFloat(e.target.value);
                  if (!isNaN(value)) {
                    onAccountChange({ leverage: value });
                  }
                }}
                className="border px-2 py-1 rounded"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Auto Trade / Trade % */}
      <Card>
        <CardContent className="space-y-2">
          <h2 className="font-semibold text-lg">General</h2>
          <div className="flex gap-20">
            <div className="flex items-center gap-4">
              <label className="w-24">Auto Trade</label>
              <input
                type="checkbox"
                checked={tokenConfig.auto_trade}
                onChange={(e) => handleInputChange(['auto_trade'], e.target.checked)}
              />
            </div>
            <div className="flex items-center gap-4">
              <label className="w-24">Trade %</label>
              {renderNumberInput(`${activeToken}-trade_pct`, ['trade_pct'], tokenConfig.trade_pct)}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Confidence Thresholds */}
      <Card>
        <CardContent>
          <h2 className="font-semibold text-lg mb-2">Confidence Thresholds</h2>
          <div className="grid grid-cols-4 gap-2">
            {Object.entries(tokenConfig.confidence_thresholds).map(([tf, val]) => (
              <div key={tf} className="flex gap-8 items-center">
                <label>{tf}</label>
                {renderNumberInput(`${activeToken}-confidence-${tf}`, ['confidence_thresholds', tf], val)}
                <PerformanceHint
                  token={activeToken}
                  fieldPath={`confidence_thresholds.${tf}`}
                  onApply={(value) => handleInputChange(['confidence_thresholds', tf], value)}
                />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Filters */}
      <Card>
        <CardContent className="space-y-4">
          <h2 className="font-semibold text-lg">Filters</h2>
          {(['base', 'macd_long', 'short_setup'] as const).map((filterKey) => {
            const filterSection = tokenConfig.filters[filterKey];
            return (
              <div key={filterKey} className="space-y-4">
                <h3 className="text-md font-semibold text-muted-foreground uppercase tracking-wide border-b pb-1">
                  {filterKey.replace('_', ' ')}
                </h3>
                <div className="grid md:grid-cols-2 gap-6">
                  {Object.entries(filterSection).map(([key, val]) => {
                    const inputKey = `${activeToken}-filter-${filterKey}-${key}`;
                    if (typeof val === 'object' && val !== null) {
                      return (
                        <div key={key} className="bg-muted p-3 rounded-lg border shadow-sm">
                          <p className="text-sm font-medium mb-2">{key}</p>
                          <div className="grid grid-cols-2 gap-3">
                            {Object.entries(val as Record<string, number>).map(([tf, v]) => (
                              <div key={tf} className="flex items-center gap-2">
                                <label className="w-10 text-xs font-medium">{tf}</label>
                                {renderNumberInput(`${inputKey}-${tf}`, ['filters', filterKey, key, tf], v)}
                                <PerformanceHint
                                  token={activeToken}
                                  fieldPath={`filters.${filterKey}.${key}.${tf}`}
                                  onApply={(value) => handleInputChange(['filters', filterKey, key, tf], value)}
                                />
                              </div>
                            ))}
                          </div>
                        </div>
                      );
                    } else {
                      return (
                        <div key={key} className="flex items-center gap-3">
                          <label className="w-48 text-sm font-medium">{key}</label>
                          {renderNumberInput(inputKey, ['filters', filterKey, key], val as number)}
                          <PerformanceHint
                            token={activeToken}
                            fieldPath={`filters.${filterKey}.${key}`}
                            onApply={(value) => handleInputChange(['filters', filterKey, key], value)}
                          />
                        </div>
                      );
                    }
                  })}
                </div>
              </div>
            );
          })}
        </CardContent>
      </Card>

      {/* Exit Strategy */}
      <Card>
        <CardContent className="space-y-2">
          <h2 className="font-semibold text-lg">Exit Strategy</h2>
          <div className="grid grid-cols-2 gap-4">
            {Object.entries(tokenConfig.exit_strategy).map(([key, val]) => {
              const inputKey = `${activeToken}-exit-${key}`;
              return (
                <div key={key} className="flex flex-col">
                  {typeof val === 'boolean' ? (
                    <div className="flex items-center gap-4">
                      <label className="capitalize text-sm">{key}</label>
                      <input
                        type="checkbox"
                        checked={val}
                        onChange={(e) => handleInputChange(['exit_strategy', key], e.target.checked)}
                      />
                      <PerformanceHint
                        token={activeToken}
                        fieldPath={`exit_strategy.${key}`}
                        onApply={(value) => handleInputChange(['exit_strategy', key], value)}
                      />
                    </div>
                  ) : (
                    <>
                      <label className="capitalize text-sm">{key}</label>
                      {renderNumberInput(inputKey, ['exit_strategy', key], val)}
                      <PerformanceHint
                        token={activeToken}
                        fieldPath={`exit_strategy.${key}`}
                        onApply={(value) => handleInputChange(['exit_strategy', key], value)}
                      />
                    </>
                  )}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
