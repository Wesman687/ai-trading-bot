'use client'
import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '@/store/store';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { updateAccountConfig } from '@/actions/accounts';
import { toast } from 'sonner';

export default function AccountPage({ params }: { params: { accountId: string } }) {
  const accountId = params.accountId;
  const dispatch = useDispatch();
  const account = useSelector((state: RootState) => state.accounts.byId[accountId]);

  const [activeToken, setActiveToken] = useState<string | null>(null);
  const [riskLevels, setRiskLevels] = useState<Record<string, number>>({});
  const [liveConfig, setLiveConfig] = useState<any>(null);

  useEffect(() => {
    if (account && !activeToken) {
      const tokens = Object.keys(account.config);
      setActiveToken(tokens[0]);
      const initialLevels: Record<string, number> = {};
      tokens.forEach(t => initialLevels[t] = 2);
      setRiskLevels(initialLevels);
      setLiveConfig(JSON.parse(JSON.stringify(account.config)));
    }
  }, [account]);

  const presets = [
    { "1m": 0.95, "15m": 0.92, "1h": 0.9, "1d": 0.88 },
    { "1m": 0.88, "15m": 0.85, "1h": 0.82, "1d": 0.8 },
    { "1m": 0.82, "15m": 0.78, "1h": 0.72, "1d": 0.67 },
    { "1m": 0.72, "15m": 0.68, "1h": 0.62, "1d": 0.57 },
    { "1m": 0.65, "15m": 0.6, "1h": 0.55, "1d": 0.5 }
  ];

  const handleInputChange = (path: string[], value: any) => {
    if (!activeToken || !liveConfig) return;
    const updated = JSON.parse(JSON.stringify(liveConfig[activeToken]));
    let nested = updated;
    for (let i = 0; i < path.length - 1; i++) nested = nested[path[i]];
    nested[path[path.length - 1]] = value;
    setLiveConfig({ ...liveConfig, [activeToken]: updated });
  };

  const applyRiskPreset = (level: number) => {
    const newThresholds = presets[level];
    handleInputChange(['confidence_thresholds'], newThresholds);
    setRiskLevels(prev => ({ ...prev, [activeToken!]: level }));
    toast.success(`${activeToken} preset level ${level + 1} applied`);
  };

  const saveConfig = () => {
    updateAccountConfig(accountId, { ...account, config: liveConfig });
    toast.success('Config saved!');
  };

  if (!account || !liveConfig || !activeToken) return <div className="text-center mt-10">Loading...</div>;
  const tokenConfig = liveConfig[activeToken];

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Config Editor: {activeToken}</h1>
        <Button variant="destructive">Cancel</Button>
      </div>

      <div className="flex gap-4 mb-4">
        {Object.keys(account.config).map((token) => (
          <Button key={token} variant={token === activeToken ? 'default' : 'outline'} onClick={() => setActiveToken(token)}>
            {token}
          </Button>
        ))}
      </div>

      <div className="mb-4">
        <label className="font-medium">Risk Level Preset</label>
        <Slider min={0} max={4} step={1} value={[riskLevels[activeToken] ?? 2]} onValueChange={([val]) => applyRiskPreset(val)} />
      </div>

      <Card><CardContent className="space-y-2">
        <h2 className="font-semibold text-lg">General</h2>
        <div className="flex items-center gap-4">
          <label className="w-24">Auto Trade</label>
          <input type="checkbox" checked={tokenConfig.auto_trade} onChange={(e) => handleInputChange(['auto_trade'], e.target.checked)} />
        </div>
        <div className="flex items-center gap-4">
          <label className="w-24">Trade %</label>
          <input type="number" step="0.01" value={tokenConfig.trade_pct} onChange={(e) => handleInputChange(['trade_pct'], parseFloat(e.target.value))} className="w-24" />
        </div>
      </CardContent></Card>

      <Card><CardContent>
        <h2 className="font-semibold text-lg mb-2">Confidence Thresholds</h2>
        <div className="grid grid-cols-4 gap-2">
          {Object.entries(tokenConfig.confidence_thresholds).map(([tf, val]) => (
            <div key={tf} className="flex flex-col">
              <label>{tf}</label>
              <input
                type="number"
                step="0.01"
                value={parseFloat(val.toFixed(2))}
                onChange={(e) => handleInputChange(['confidence_thresholds', tf], parseFloat(e.target.value))}
                className="bg-black border px-2 py-1 rounded"
              />
            </div>
          ))}
        </div>
      </CardContent></Card>

      <Card><CardContent className="space-y-4">
        <h2 className="font-semibold text-lg">Filters</h2>

        {['base', 'macd_long', 'short_setup'].map((filterKey) => (
          <div key={filterKey} className="space-y-2">
            <h3 className="font-semibold capitalize text-muted-foreground mb-1">{filterKey.replace('_', ' ')}</h3>
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(tokenConfig.filters[filterKey]).map(([key, val]) => (
                typeof val === 'object' ? (
                  <div key={key}>
                    <p className="font-medium text-sm mb-1">{key}</p>
                    <div className="grid grid-cols-2 gap-2">
                      {Object.entries(val).map(([tf, v]) => (
                        <div key={tf} className="flex flex-col">
                          <label className="text-xs">{tf}</label>
                          <input
                            type="number"
                            step="0.01"
                            value={parseFloat(v.toFixed(2))}
                            onChange={(e) => handleInputChange(['filters', filterKey, key, tf], parseFloat(e.target.value))}
                            className="bg-black border px-2 py-1 rounded"
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div key={key} className="flex flex-col">
                    <label className="text-sm">{key}</label>
                    <input
                      type="number"
                      step="0.01"
                      value={parseFloat(val.toFixed(2))}
                      onChange={(e) => handleInputChange(['filters', filterKey, key], parseFloat(e.target.value))}
                      className="bg-black border px-2 py-1 rounded"
                    />
                  </div>
                )
              ))}
            </div>
          </div>
        ))}
      </CardContent></Card>

      <Card><CardContent className="space-y-2">
        <h2 className="font-semibold text-lg">Exit Strategy</h2>
        <div className="grid grid-cols-2 gap-4">
          {Object.entries(tokenConfig.exit_strategy).map(([key, val]) => (
            <div key={key} className="flex flex-col">
              <label className="capitalize text-sm">{key}</label>
              {typeof val === 'boolean' ? (
                <input type="checkbox" checked={val} onChange={(e) => handleInputChange(['exit_strategy', key], e.target.checked)} />
              ) : (
                <input
                  type="number"
                  step="0.01"
                  value={parseFloat(val.toFixed(2))}
                  onChange={(e) => handleInputChange(['exit_strategy', key], parseFloat(e.target.value))}
                  className="bg-black border px-2 py-1 rounded"
                />
              )}
            </div>
          ))}
        </div>
      </CardContent></Card>

      <div className="text-right">
        <Button onClick={saveConfig}>Save Config</Button>
      </div>
    </div>
  );
}
