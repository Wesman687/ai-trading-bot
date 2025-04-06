'use client';
import { RootState } from '@/store/store';
import Link from 'next/link';
import { useSelector } from 'react-redux';

export default function Sidebar() {
  
  const availableTokens = useSelector((state: RootState) => state.accounts.availableTokens);

  return (
    <aside className="w-64 bg-muted p-4 shadow-xl h-full">
      <h1 className="text-xl font-bold mb-6">📊 Trader Panel</h1>

      <nav className="flex flex-col space-y-2">
        <Link href="/" className="hover:text-blue-500 font-medium">
          🏠 Home
        </Link>
        
        <Link href="/account" className="hover:text-green-600 font-medium">
          ➕ New Account
        </Link>

        <p className="text-sm mt-4 text-muted-foreground">Tokens</p>
        {availableTokens.map(token => (
          <Link
            key={token}
            href={`/token-stats/${token}`}
            className="hover:text-blue-500"
          >
            {token}
          </Link>
        ))}
      </nav>
    </aside>
  );
}