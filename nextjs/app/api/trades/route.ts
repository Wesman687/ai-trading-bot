'use server'
import { mockTrades } from '@/lib/mockData';
import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({ trades: mockTrades });
}