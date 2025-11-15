'use client'

import { useState } from 'react'
import { checkDiningBalance, useDiningBalance, libraryCheckout, residenceAccess } from '@/lib/api'

interface ServiceCardProps {
  title: string
  description: string
  icon: string
  serviceType: 'dining' | 'library' | 'residence'
}

export default function ServiceCard({ title, description, icon, serviceType }: ServiceCardProps) {
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [balance, setBalance] = useState<number | null>(null)

  const handleAction = async () => {
    setLoading(true)
    setMessage('')
    
    try {
      switch (serviceType) {
        case 'dining':
          const balanceData = await checkDiningBalance()
          setBalance(balanceData.balance)
          setMessage(`Current balance: $${balanceData.balance.toFixed(2)}`)
          break
        case 'library':
          await libraryCheckout()
          setMessage('Library checkout validated successfully!')
          break
        case 'residence':
          await residenceAccess()
          setMessage('Residence hall access granted!')
          break
      }
    } catch (error: any) {
      setMessage(error.response?.data?.detail || 'Action failed')
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
            <div className={`mb-4 p-3 rounded-lg text-sm ${
              message.includes('success') || message.includes('Balance')
                ? 'bg-green-50 text-green-700'
                : 'bg-red-50 text-red-700'
            }`}>
              {message}
            </div>
          )}
          
          <button
            onClick={handleAction}
            disabled={loading}
            className="bg-uw-red text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-uw-red-dark transition-colors disabled:opacity-50"
          >
            {loading ? 'Processing...' : serviceType === 'dining' ? 'Check Balance' : 'Access Service'}
          </button>
        </div>
      </div>
    </div>
  )
}

