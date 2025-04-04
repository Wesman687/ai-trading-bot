// app/account/[accountId]/config/page.tsx
import { use } from 'react';
import AccountConfigClientWrapper from './AccountConfigClientWrapper';

export default function Page({ params }: { params: Promise<{ accountId: string }> }) {
  const { accountId } = use(params);
  return <AccountConfigClientWrapper accountId={accountId} />;
}