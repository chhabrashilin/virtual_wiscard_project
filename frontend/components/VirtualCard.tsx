'use client'

import { useEffect, useState } from 'react'
import { getMyCard } from '@/lib/api'

interface CardData {
  full_name: string
  student_id: string
  netid: string
  email: string
  photo_url: string
  is_active: boolean
  expiration_date: string
  balances: Record<string, number>
}

export default function VirtualCard() {
  const [cardData, setCardData] = useState<CardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadCard()
  }, [])

  const loadCard = async () => {
    try {
      const data = await getMyCard()
      setCardData(data)
    } catch (error) {
      console.error('Failed to load card:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-uw-red"></div>
      </div>
    )
  }

  if (!cardData) {
    return <div className="text-center text-red-600">Failed to load card data</div>
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden border-2 border-uw-red">
      {/* Header */}
      <div className="bg-uw-red text-white p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Virtual Wiscard</h2>
            <p className="text-sm opacity-90">University of Wisconsin-Madison</p>
          </div>
          <div className="text-right">
            <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
              cardData.is_active ? 'bg-green-500' : 'bg-red-500'
            }`}>
              {cardData.is_active ? 'ACTIVE' : 'INACTIVE'}
            </div>
          </div>
        </div>
      </div>

      {/* Card Body */}
      <div className="p-6">
        <div className="flex items-start space-x-4 mb-6">
          {/* Photo placeholder */}
          <div className="w-24 h-24 bg-gray-200 rounded-lg flex items-center justify-center">
            {cardData.photo_url ? (
              <img src={cardData.photo_url} alt={cardData.full_name} className="w-full h-full object-cover rounded-lg" />
            ) : (
              <span className="text-3xl text-gray-400">👤</span>
            )}
          </div>

          {/* Student Info */}
          <div className="flex-1">
            <h3 className="text-xl font-bold text-gray-800 mb-1">{cardData.full_name}</h3>
            <p className="text-sm text-gray-600 mb-2">Student ID: {cardData.student_id}</p>
            <p className="text-sm text-gray-600 mb-2">NetID: {cardData.netid}</p>
            <p className="text-sm text-gray-600">{cardData.email}</p>
          </div>
        </div>

        {/* Expiration */}
        <div className="border-t pt-4">
          <p className="text-sm text-gray-600">
            <span className="font-semibold">Expires:</span> {formatDate(cardData.expiration_date)}
          </p>
        </div>

        {/* Balances */}
        {Object.keys(cardData.balances).length > 0 && (
          <div className="border-t pt-4 mt-4">
            <p className="text-sm font-semibold text-gray-700 mb-2">Balances:</p>
            <div className="space-y-1">
              {Object.entries(cardData.balances).map(([service, balance]) => (
                <div key={service} className="flex justify-between text-sm">
                  <span className="text-gray-600 capitalize">{service}:</span>
                  <span className="font-semibold text-uw-red">${balance.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

