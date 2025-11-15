'use client'

import { useState } from 'react'
import { QRCodeSVG } from 'qrcode.react'
import { generateQRCode } from '@/lib/api'

export default function QRCodeDisplay() {
  const [qrData, setQrData] = useState<string | null>(null)
  const [expiresAt, setExpiresAt] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

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
          <p className="text-sm text-gray-600 mb-2">
            Expires at: <span className="font-semibold">{expiresAt && formatExpiry(expiresAt)}</span>
          </p>
          <p className="text-xs text-gray-500 mb-4">
            This QR code is valid for 5 minutes
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

