'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { toast } from 'sonner'

export default function CreateAccountPage() {
  const router = useRouter()
  const [accountId, setAccountId] = useState('')
  const [name, setName] = useState('')
  const [balance, setBalance] = useState(10000)
  const [leverage, setLeverage] = useState(1.5)
  const [riskPct, setRiskPct] = useState(0.15)
  const [tradeSize, setTradeSize] = useState(1000)

  const handleSubmit = async () => {
    if (!accountId) return toast.error("Account ID required")

    const res = await fetch(`/api/account/${accountId}/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name,
        balance,
        leverage,
        trade_risk_pct: riskPct,
        trade_size: tradeSize,
        config: null // or send a custom config object
      }),
    })

    if (res.ok) {
      toast.success('Account created!')
      router.push(`/account/${accountId}/config`)
    } else {
      const err = await res.json()
      toast.error(`Failed: ${err.detail}`)
    }
  }

  return (
    <div className="p-6 space-y-4 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold">Create New Account</h1>
      <input placeholder="Account ID" value={accountId} onChange={e => setAccountId(e.target.value)} className="w-full px-3 py-2 border rounded" />
      <input placeholder="Name" value={name} onChange={e => setName(e.target.value)} className="w-full px-3 py-2 border rounded" />
      <input type="number" value={balance} onChange={e => setBalance(+e.target.value)} className="w-full px-3 py-2 border rounded" />
      <input type="number" step="0.01" value={riskPct} onChange={e => setRiskPct(+e.target.value)} className="w-full px-3 py-2 border rounded" />
      <input type="number" value={tradeSize} onChange={e => setTradeSize(+e.target.value)} className="w-full px-3 py-2 border rounded" />
      <Button onClick={handleSubmit}>Create</Button>
    </div>
  )
}
