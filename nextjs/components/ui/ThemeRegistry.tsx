// components/ThemeRegistry.tsx
'use client';

import { ThemeProvider } from 'next-themes';

export function ThemeRegistry({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="dark"
      enableSystem
      disableTransitionOnChange
    >
      {children}
    </ThemeProvider>
  );
}
