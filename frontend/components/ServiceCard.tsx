'use client'

import { useState } from 'react'
import toast from 'react-hot-toast'
import {
  checkDiningBalance,
  useDiningBalance,
  checkPrintBalance,
  usePrintBalance,
  libraryCheckout,
  residenceAccess,
} from '@/lib/api'

type ServiceType = 'dining' | 'library' | 'residence' | 'print'

interface ServiceCardProps {
  title: string
  description: string
  icon: string
  serviceType: ServiceType
}

const SPENDABLE: ServiceType[] = ['dining', 'print']

export default function ServiceCard({ title, description, icon, serviceType }: ServiceCardProps) {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [isError, setIsError] = useState(false)
  const [balance, setBalance] = useState<number | null>(null)
  const [amount, setAmount] = useState('')

  const spendable = SPENDABLE.includes(serviceType)

  const setOk = (msg: string) => {
    setMessage(msg)
    setIsError(false)
  }
  const setErr = (msg: string) => {
    setMessage(msg)
    setIsError(true)
  }

  const handleCheck = async () => {
    setLoading(true)
    setMessage('')
    try {
      switch (serviceType) {
        case 'dining': {
          const data = await checkDiningBalance()
          setBalance(data.balance)
          setOk(`Current balance: $${data.balance.toFixed(2)}`)
          break
        }
        case 'print': {
          const data = await checkPrintBalance()
          setBalance(data.balance)
          setOk(`Current balance: $${data.balance.toFixed(2)}`)
          break
        }
        case 'library':
          await libraryCheckout()
          setOk('Library checkout validated successfully!')
          break
        case 'residence':
          await residenceAccess()
          setOk('Residence hall access granted!')
          break
      }
    } catch (error: any) {
      setErr(error.response?.data?.detail || 'Action failed')
    } finally {
      setLoading(false)
    }
  }

  const handleSpend = async () => {
    const value = parseFloat(amount)
    if (!value || value <= 0) {
      toast.error('Enter a valid amount')
      return
    }
    setLoading(true)
    setMessage('')
    try {
      const data =
        serviceType === 'dining'
          ? await useDiningBalance(value)
          : await usePrintBalance(value)
      setBalance(data.new_balance)
      setAmount('')
      setOk(`Charged $${data.amount_charged.toFixed(2)}. New balance: $${data.new_balance.toFixed(2)}`)
      toast.success(`Charged $${data.amount_charged.toFixed(2)}`)
    } catch (error: any) {
      setErr(error.response?.data?.detail || 'Transaction failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200 hover:shadow-lg transition-shadow">
      <div className="flex items-start space-x-4">
        <div className="text-4xl">{icon}</div>
        <div className="flex-1">
          <h4 className="text-lg font-bold text-gray-800 mb-1">{title}</h4>
          <p className="text-sm text-gray-600 mb-4">{description}</p>

          {balance !== null && (
            <div className="mb-4 p-3 bg-uw-red/10 rounded-lg">
              <p className="text-sm font-semibold text-uw-red">
                Balance: ${balance.toFixed(2)}
              </p>
            </div>
          )}

          {message && (
            <div
              className={`mb-4 p-3 rounded-lg text-sm ${
                isError ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'
              }`}
            >
              {message}
            </div>
          )}

          {spendable && (
            <div className="flex items-center space-x-2 mb-3">
              <input
                type="number"
                step="0.01"
                min="0"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="Amount"
                className="w-24 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-uw-red focus:border-transparent"
              />
              <button
                onClick={handleSpend}
                disabled={loading || !amount}
                className="bg-uw-red text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-uw-red-dark transition-colors disabled:opacity-50"
              >
                {serviceType === 'dining' ? 'Pay' : 'Print'}
              </button>
            </div>
          )}

          <button
            onClick={handleCheck}
            disabled={loading}
            className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg text-sm font-semibold hover:bg-gray-200 transition-colors disabled:opacity-50"
          >
            {loading
              ? 'Processing...'
              : spendable
              ? 'Check Balance'
              : 'Access Service'}
          </button>
        </div>
      </div>
    </div>
  )
}
