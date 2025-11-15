'use client'

import { useState, useEffect } from 'react'
import { QRCodeSVG } from 'qrcode.react'
import { generateQRCode } from '@/lib/api'

export default function QRCodeDisplay() {
  const [qrData, setQrData] = useState<string | null>(null)
  const [expiresAt, setExpiresAt] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [timeRemaining, setTimeRemaining] = useState<number>(0)

  // Countdown timer effect
  useEffect(() => {
    if (!expiresAt) return

    const calculateTimeRemaining = () => {
      const now = new Date().getTime()
      const expiry = new Date(expiresAt).getTime()
      const remaining = Math.max(0, Math.floor((expiry - now) / 1000))
      return remaining
    }

    setTimeRemaining(calculateTimeRemaining())

    const interval = setInterval(() => {
      const remaining = calculateTimeRemaining()
      setTimeRemaining(remaining)

      if (remaining === 0) {
        clearInterval(interval)
        // Auto-clear QR code when expired
        setQrData(null)
        setExpiresAt(null)
      }
    }, 1000)

    return () => clearInterval(interval)
  }, [expiresAt])

  const handleGenerate = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await generateQRCode()
      setQrData(data.token)
      setExpiresAt(data.expires_at)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate QR code')
    } finally {
      setLoading(false)
    }
  }

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const getProgressPercentage = (): number => {
    return (timeRemaining / 300) * 100 // 300 seconds = 5 minutes
  }

  const formatExpiry = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 border-2 border-uw-red">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Access QR Code</h3>
      
      {!qrData ? (
        <div className="text-center py-8">
          <p className="text-gray-600 mb-4">Generate a temporary QR code for scanning</p>
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="bg-uw-red text-white px-6 py-3 rounded-lg font-semibold hover:bg-uw-red-dark transition-colors disabled:opacity-50"
          >
            {loading ? 'Generating...' : 'Generate QR Code'}
          </button>
          {error && (
            <p className="text-red-600 text-sm mt-4">{error}</p>
          )}
        </div>
      ) : (
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <div className="bg-white p-4 rounded-lg border-2 border-gray-200">
              <QRCodeSVG value={qrData} size={200} />
            </div>
          </div>

          {/* Countdown Timer */}
          <div className="mb-4">
            <div className="text-2xl font-bold text-uw-red mb-2">
              {formatTime(timeRemaining)}
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5 mb-2">
              <div
                className={`h-2.5 rounded-full transition-all duration-1000 ${
                  timeRemaining < 60 ? 'bg-red-600' : timeRemaining < 120 ? 'bg-yellow-500' : 'bg-green-600'
                }`}
                style={{ width: `${getProgressPercentage()}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-500">
              {timeRemaining < 60 ? '⚠️ Expiring soon!' : 'Time remaining'}
            </p>
          </div>

          <p className="text-sm text-gray-600 mb-2">
            Expires at: <span className="font-semibold">{expiresAt && formatExpiry(expiresAt)}</span>
          </p>
          <button
            onClick={handleGenerate}
            className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm font-semibold hover:bg-gray-300 transition-colors"
          >
            Generate New Code
          </button>
        </div>
      )}
    </div>
  )
}

