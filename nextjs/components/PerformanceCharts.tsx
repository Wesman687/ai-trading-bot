// components/PerformanceCharts.tsx
'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import { API_BASE } from '@/lib/config';

interface PerformanceStats {
  total_pnl: number;
  total_trades: number;
  win_count: number;
  loss_count: number;
  avg_duration_minutes: number;
  win_rate: number;
  avg_pnl: number;
  sharpe_ratio: number;
  pnl_distribution: number[];
  duration_distribution: Record<string, number>;
  by_token: Record<string, { pnl: number; wins: number; losses: number }>;
  by_day: Record<string, { pnl: number; trades: number }>;
  by_hour: Record<string, { pnl: number; trades: number }>;
}

export default function PerformanceCharts({ accountId }: { accountId: string }) {
  const [performance, setPerformance] = useState<PerformanceStats | null>(null);
  const [selectedToken, setSelectedToken] = useState<string>('');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');

  useEffect(() => {
    const query = new URLSearchParams();
    if (selectedToken) query.append('token', selectedToken);
    if (startDate) query.append('start', startDate);
    if (endDate) query.append('end', endDate);

    fetch(`${API_BASE}/account/${accountId}/performance?${query.toString()}`)
      .then((res) => res.json())
      .then((data) => setPerformance(data));
  }, [accountId, selectedToken, startDate, endDate]);

  if (!performance) return <div className="text-sm">Loading performance data...</div>;

  const tokenData = Object.entries(performance.by_token || {}).map(([token, stats]) => ({
    token,
    pnl: stats.pnl,
    wins: stats.wins,
    losses: stats.losses,
  }));

  const dailyData = Object.entries(performance.by_day || {}).map(([day, d]) => ({
    date: day,
    pnl: d.pnl,
    trades: d.trades,
  }));

  const hourlyData = Object.entries(performance.by_hour || {}).map(([hour, d]) => ({
    hour,
    pnl: d.pnl,
    trades: d.trades,
  }));

  const pnlHistogram = Array.isArray(performance.pnl_distribution)
    ? performance.pnl_distribution.map((count, i) => ({ bin: i, count }))
    : [];

  const durationHistogram = Object.entries(performance.duration_distribution || {}).map(
    ([duration, count]) => ({ bin: parseInt(duration), count })
  );

  return (
    <div className="space-y-6">
      <Card>
        <CardContent className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="text-sm">Token</label>
            <input
              type="text"
              className="w-full rounded border px-2 py-1"
              value={selectedToken}
              onChange={(e) => setSelectedToken(e.target.value)}
              placeholder="e.g. BTC"
            />
          </div>
          <div>
            <label className="text-sm">Start Date</label>
            <input
              type="date"
              className="w-full rounded border px-2 py-1"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>
          <div>
            <label className="text-sm">End Date</label>
            <input
              type="date"
              className="w-full rounded border px-2 py-1"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Win Rate</p>
            <p className="text-lg font-semibold">{performance.win_rate.toFixed(2)}%</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Avg PnL</p>
            <p className="text-lg font-semibold">${performance.avg_pnl.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Avg Duration</p>
            <p className="text-lg font-semibold">{performance.avg_duration_minutes} mins</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Sharpe Ratio</p>
            <p className="text-lg font-semibold">{performance.sharpe_ratio.toFixed(2)}</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <h2 className="text-xl font-semibold mb-4">PnL by Token</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={tokenData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="token" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="pnl" fill="#4ade80" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <h2 className="text-xl font-semibold mb-4">PnL Over Time (Daily)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={dailyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="pnl" stroke="#60a5fa" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <h2 className="text-xl font-semibold mb-4">Hourly Performance</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={hourlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="pnl" fill="#f97316" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <h2 className="text-xl font-semibold mb-4">PnL Histogram</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={pnlHistogram}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="bin" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#34d399" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <h2 className="text-xl font-semibold mb-4">Trade Duration Histogram</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={durationHistogram}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="bin" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#facc15" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
