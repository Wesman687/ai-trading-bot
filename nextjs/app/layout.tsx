'use client'
import { Inter } from 'next/font/google';
import './globals.css';
const inter = Inter({ subsets: ['latin'] });
import { ReduxProvider } from '@/providers/ReduxProvider';
import { ThemeRegistry } from '@/components/ui/ThemeRegistry';


export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-background text-foreground`}>
      <ReduxProvider>
        <ThemeRegistry>
          <div className="flex h-screen">
            <aside className="w-64 bg-muted p-4 shadow-xl">
              <h1 className="text-xl font-bold mb-4">📊 Accounts</h1>
              {/* Sidebar: dynamic account nav here */}
            </aside>
            <main className="flex-1 overflow-y-auto p-6">
              {children}
            </main>
          </div>
        </ThemeRegistry>
      </ReduxProvider>
      </body>
    </html>
  );
}