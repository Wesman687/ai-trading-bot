import { useSelector } from 'react-redux';
import { RootState } from '@/store/store';
import { Trade } from '@/types/account';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';

export default function TokenStatsChart({ token }: { token: string }) {
  const trades = useSelector((state: RootState) =>
    Object.values(state.trades.byId).filter((t: Trade) => t.token === token && t.exit_time && t.pnl !== undefined)
  );

  const chartData = trades.map((t) => ({
    date: format(new Date(t.exit_time!), 'MM-dd HH:mm'),
    pnl: t.pnl,
  }));

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="pnl" stroke="#8884d8" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}