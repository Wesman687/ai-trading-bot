// app/account/[accountId]/config/AccountConfigClientWrapper.tsx
'use client'

import dynamic from 'next/dynamic';

// ✅ Dynamically load the true client component, disabling SSR
const AccountConfigClient = dynamic(() => import('./AccountConfigClient'), {
  ssr: false,
});

export default function AccountConfigClientWrapper({ accountId }: { accountId: string }) {
  return <AccountConfigClient accountId={accountId} />;
}