'use client'

import { useState, useEffect } from 'react'
import { getTransactionHistory } from '@/lib/api'

interface Transaction {
  id: number
  service_type: string
  action: string
  success: boolean
  location: string | null
  created_at: string
}

export default function TransactionHistory() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadTransactions()
  }, [])

  const loadTransactions = async () => {
    try {
      setLoading(true)
      const data = await getTransactionHistory()
      setTransactions(data.transactions)
      setError('')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load transaction history')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getServiceIcon = (serviceType: string) => {
    switch (serviceType) {
      case 'dining':
        return '🍽️'
      case 'library':
        return '📚'
      case 'residence':
        return '🏠'
      case 'print':
        return '🖨️'
      default:
        return '📋'
    }
  }

  const getServiceColor = (serviceType: string) => {
    switch (serviceType) {
      case 'dining':
        return 'bg-orange-100 text-orange-800'
      case 'library':
        return 'bg-blue-100 text-blue-800'
      case 'residence':
        return 'bg-green-100 text-green-800'
      case 'print':
        return 'bg-purple-100 text-purple-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-bold text-gray-800">Recent Activity</h3>
        <button
          onClick={loadTransactions}
          className="text-uw-red text-sm hover:underline"
        >
          Refresh
        </button>
      </div>

      {loading && (
        <div className="text-center py-8 text-gray-500">Loading...</div>
      )}

      {error && (
        <div className="text-center py-4 text-red-600 text-sm">{error}</div>
      )}

      {!loading && !error && transactions.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No transaction history yet
        </div>
      )}

      {!loading && !error && transactions.length > 0 && (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {transactions.map((transaction) => (
            <div
              key={transaction.id}
              className="border-b border-gray-200 pb-3 last:border-b-0 hover:bg-gray-50 p-2 rounded transition-colors"
            >
              <div className="flex justify-between items-start">
                <div className="flex items-start space-x-3">
                  <span className="text-2xl">{getServiceIcon(transaction.service_type)}</span>
                  <div>
                    <div className="flex items-center space-x-2">
                      <span
                        className={`inline-block px-2 py-1 rounded text-xs font-semibold ${getServiceColor(
                          transaction.service_type
                        )}`}
                      >
                        {transaction.service_type.toUpperCase()}
                      </span>
                      {transaction.success ? (
                        <span className="text-green-600 text-xs">✓ Success</span>
                      ) : (
                        <span className="text-red-600 text-xs">✗ Failed</span>
                      )}
                    </div>
                    <p className="text-sm text-gray-700 mt-1 font-medium">
                      {transaction.action.replace(/_/g, ' ')}
                    </p>
                    {transaction.location && (
                      <p className="text-xs text-gray-500 mt-1">
                        📍 {transaction.location}
                      </p>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-500">
                    {formatDate(transaction.created_at)}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
