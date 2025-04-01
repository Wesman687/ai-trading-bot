import { ThemeRegistry } from '@/components/ThemeRegistry';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="flex flex-col min-h-screen justify-center items-center">
          <div className="w-fit">
            <ThemeRegistry>
              {children}
            </ThemeRegistry>
          </div>
        </div>
      </body>
    </html>
  );
}