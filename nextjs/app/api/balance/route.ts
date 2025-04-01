'use server'
import { mockBalance } from '@/lib/mockData';
import { NextResponse } from 'next/server';


export async function GET() {
  return NextResponse.json({ balance: mockBalance });
}