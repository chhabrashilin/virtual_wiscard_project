'use client'

import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { checkWiscardCash, useWiscardCash } from '@/lib/api'

export default function WiscardCashCard() {
  const [balance, setBalance] = useState<number | null>(null)
  const [amount, setAmount] = useState('')
  const [vendor, setVendor] = useState('Vending Machine')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    load()
  }, [])

  const load = async () => {
    try {
      const data = await checkWiscardCash()
      setBalance(data.balance)
    } catch {
      /* ignore */
    }
  }

  const handleSpend = async () => {
    const value = parseFloat(amount)
    if (!value || value <= 0) {
      toast.error('Enter a valid amount')
      return
    }
    setLoading(true)
    try {
      const data = await useWiscardCash(value, vendor)
      setBalance(data.new_balance)
      setAmount('')
      toast.success(`Paid $${data.amount_charged.toFixed(2)} at ${data.vendor}`)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Payment failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-gradient-to-br from-uw-red to-uw-red-dark rounded-xl shadow-lg p-6 text-white">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold">💳 Wiscard Cash</h3>
        <span className="text-xs opacity-80">Vending · Laundry · Bookstore · Off-campus</span>
      </div>

      <p className="text-4xl font-bold mb-1">
        {balance !== null ? `$${balance.toFixed(2)}` : '—'}
      </p>
      <p className="text-xs opacity-80 mb-5">Available balance</p>

      <div className="bg-white/10 rounded-lg p-3 backdrop-blur space-y-3">
        <select
          value={vendor}
          onChange={(e) => setVendor(e.target.value)}
          className="w-full px-3 py-2 rounded-lg bg-white/90 text-gray-800 text-sm"
        >
          <option>Vending Machine</option>
          <option>Laundry</option>
          <option>University Bookstore</option>
          <option>Off-campus Partner</option>
        </select>
        <div className="flex items-center space-x-2">
          <input
            type="number"
            step="0.01"
            min="0"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="Amount"
            className="w-24 px-3 py-2 rounded-lg text-gray-800 text-sm"
          />
          <button
            onClick={handleSpend}
            disabled={loading || !amount}
            className="flex-1 bg-white text-uw-red px-4 py-2 rounded-lg text-sm font-bold hover:bg-gray-100 transition-colors disabled:opacity-50"
          >
            {loading ? 'Processing…' : 'Pay'}
          </button>
        </div>
      </div>
    </div>
  )
}
