'use client';
import Link from 'next/link';

export default function Sidebar() {
  return (
    <aside className="w-64 bg-muted p-4 shadow-xl h-full">
      <h1 className="text-xl font-bold mb-6">📊 Trader Panel</h1>

      <nav className="flex flex-col space-y-2">
        <Link href="/" className="hover:text-blue-500 font-medium">
          🏠 Home
        </Link>

        {/* 📁 Future sections can go here */}
        {/* <Link href="/settings">⚙️ Settings</Link> */}
        {/* <Link href="/logs">📝 Logs</Link> */}
      </nav>
    </aside>
  );
}
