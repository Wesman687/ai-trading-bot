'use client';

import { ThemeProvider, CssBaseline, createTheme } from '@mui/material';

const theme = createTheme(); // can safely be used here

export function ThemeRegistry({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
}