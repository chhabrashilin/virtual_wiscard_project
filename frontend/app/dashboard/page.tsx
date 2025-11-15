'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { getToken, getCurrentUser } from '@/lib/api'
import VirtualCard from '@/components/VirtualCard'
import QRCodeDisplay from '@/components/QRCodeDisplay'
import ServiceCard from '@/components/ServiceCard'
import TransactionHistory from '@/components/TransactionHistory'
import BlockchainCard from '@/components/BlockchainCard'
import { Toaster } from 'react-hot-toast'

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    const token = getToken()
    if (!token) {
      router.push('/login')
      return
    }

    try {
      const userData = await getCurrentUser()
      setUser(userData)
    } catch (error) {
      router.push('/login')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-uw-red"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />

      {/* Header */}
      <header className="bg-uw-red text-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">Virtual Wiscard 2.0</h1>
              <p className="text-sm opacity-90">Welcome, {user?.full_name}</p>
            </div>
            <div className="flex items-center space-x-4">
              {user?.is_admin && (
                <button
                  onClick={() => router.push('/admin')}
                  className="bg-white text-uw-red px-4 py-2 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
                >
                  Admin Panel
                </button>
              )}
              <button
                onClick={handleLogout}
                className="bg-uw-red-dark px-4 py-2 rounded-lg font-semibold hover:bg-opacity-90 transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Virtual Card & QR Code */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <VirtualCard />
          <QRCodeDisplay />
        </div>

        {/* Blockchain & Apple Wallet */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <BlockchainCard />
          <TransactionHistory />
        </div>

        {/* Services */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Campus Services</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <ServiceCard
              title="Dining Halls"
              description="Check your dining balance and access meal services"
              icon="🍽️"
              serviceType="dining"
            />
            <ServiceCard
              title="Libraries"
              description="Validate library checkout and access"
              icon="📚"
              serviceType="library"
            />
            <ServiceCard
              title="Residence Halls"
              description="Access residence hall doors and facilities"
              icon="🏠"
              serviceType="residence"
            />
          </div>
        </div>
      </main>
    </div>
  )
}

