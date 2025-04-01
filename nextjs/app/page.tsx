'use client'
import { useEffect, useState } from 'react';
import axios from 'axios';
import { Container, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';

interface Trade {
  id: number;
  type: string;
  amount: number;
  price: number;
  timestamp: string;
}

const Dashboard = () => {
  const [balance, setBalance] = useState<number>(0);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [pnl, setPnL] = useState<number>(0);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const balanceResponse = await axios.get('/api/balance');
        setBalance(balanceResponse.data.balance);

        const tradesResponse = await axios.get('/api/trades');
        setTrades(tradesResponse.data.trades);

        const pnlResponse = await axios.get('/api/pnl');
        setPnL(pnlResponse.data.pnl);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);

  return (
    <Container className='bg-black rounded-2xl  w-fit text-red-500 p-4'>
      <Typography variant="h4" component="h1" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="h6" component="h2" gutterBottom>
        Balance: ${balance.toFixed(2)}
      </Typography>
      <Typography variant="h6" component="h2" gutterBottom>
        PnL: ${pnl.toFixed(2)}
      </Typography>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>Price</TableCell>
              <TableCell>Timestamp</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {trades.map((trade) => (
              <TableRow key={trade.id}>
                <TableCell>{trade.id}</TableCell>
                <TableCell>{trade.type}</TableCell>
                <TableCell>{trade.amount}</TableCell>
                <TableCell>${trade.price.toFixed(2)}</TableCell>
                <TableCell>{trade.timestamp}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
};

export default Dashboard;