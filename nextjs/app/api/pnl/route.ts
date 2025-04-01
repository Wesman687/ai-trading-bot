'use server'
import { NextResponse } from 'next/server';
import { mockBalance, mockTrades, calculatePnL } from '@/lib/mockData';

export async function GET() {
  const pnl = calculatePnL(mockTrades, mockBalance);
  return NextResponse.json({ pnl });
}