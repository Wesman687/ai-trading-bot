'use client'
import { Inter } from 'next/font/google';
import './globals.css';
const inter = Inter({ subsets: ['latin'] });
import { ReduxProvider } from '@/providers/ReduxProvider';
import { ThemeRegistry } from '@/components/ui/ThemeRegistry';
import Sidebar from '@/components/layout/SideBar';


export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-background text-foreground`}>
      <ReduxProvider>
        <ThemeRegistry>
          <div className="flex h-screen">
            <Sidebar />
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