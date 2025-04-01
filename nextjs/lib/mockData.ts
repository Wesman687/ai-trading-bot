
export const mockBalance = 10000; // Starting balance

export const mockTrades = [
  { id: 1, type: 'buy', amount: 0.5, price: 30000, timestamp: '2023-10-01T12:00:00Z' },
  { id: 2, type: 'sell', amount: 0.5, price: 31000, timestamp: '2023-10-02T12:00:00Z' },
];

export const calculatePnL = (trades: typeof mockTrades, balance: number) => {
  let pnl = balance - mockBalance;
  trades.forEach((trade) => {
    if (trade.type === 'sell') {
      pnl += trade.amount * trade.price;
    } else {
      pnl -= trade.amount * trade.price;
    }
  });
  return pnl;
};