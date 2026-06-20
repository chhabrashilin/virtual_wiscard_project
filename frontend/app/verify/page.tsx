'use client'

import { useEffect, useRef, useState } from 'react'
import Link from 'next/link'
import { verifyAccessToken, validateTicket } from '@/lib/api'

interface VerifiedUser {
  full_name: string
  student_id: string
  netid: string
}

interface VerifyResult {
  success: boolean
  user?: VerifiedUser
  service_type?: string
  action?: string
  resource_name?: string | null
  // ticket results
  event_name?: string
  venue?: string
  seat?: string | null
  holder?: { full_name: string; student_id: string }
}

const SERVICES = [
  { value: 'dining', label: 'Dining', icon: '🍽️' },
  { value: 'wiscard_cash', label: 'Wiscard Cash', icon: '💳' },
  { value: 'transit', label: 'Transit', icon: '🚌' },
  { value: 'door', label: 'Door Access', icon: '🚪' },
  { value: 'ticket', label: 'Event Ticket', icon: '🎟️' },
]

const RESOURCES = [
  { value: 'recwell', label: 'RecWell (Nick & Bakke)' },
  { value: 'sellery_hall', label: 'Sellery Residence Hall' },
  { value: 'witte_hall', label: 'Witte Residence Hall' },
  { value: 'chadbourne_hall', label: 'Chadbourne Residence Hall' },
  { value: 'chem_lab', label: 'Chemistry Lab 301' },
]

export default function VerifyPage() {
  const [token, setToken] = useState('')
  const [serviceType, setServiceType] = useState('dining')
  const [resource, setResource] = useState('recwell')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<VerifyResult | null>(null)
  const [error, setError] = useState('')
  const [scanning, setScanning] = useState(false)
  const [scanError, setScanError] = useState('')

  const videoRef = useRef<HTMLVideoElement>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const rafRef = useRef<number | null>(null)
  const serviceTypeRef = useRef(serviceType)
  const resourceRef = useRef(resource)

  useEffect(() => {
    serviceTypeRef.current = serviceType
  }, [serviceType])

  useEffect(() => {
    resourceRef.current = resource
  }, [resource])

  const submitToken = async (raw: string) => {
    const value = raw.trim()
    if (!value) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const svc = serviceTypeRef.current
      if (svc === 'ticket') {
        const data = await validateTicket(value)
        setResult({ success: true, service_type: 'ticket', ...data })
      } else {
        const data = await verifyAccessToken(
          value,
          svc,
          svc === 'transit' ? 'tap' : 'entry',
          svc === 'door' ? resourceRef.current : null
        )
        setResult(data)
      }
      setToken('')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid or expired access code')
    } finally {
      setLoading(false)
    }
  }

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault()
    await submitToken(token)
  }

  const stopScan = () => {
    if (rafRef.current) cancelAnimationFrame(rafRef.current)
    rafRef.current = null
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop())
      streamRef.current = null
    }
    setScanning(false)
  }

  const startScan = async () => {
    setScanError('')
    if (typeof window === 'undefined' || !window.BarcodeDetector) {
      setScanError(
        'Camera scanning is not supported in this browser. Paste the token instead (works everywhere).'
      )
      return
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' },
      })
      streamRef.current = stream
      setScanning(true)
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        await videoRef.current.play()
      }
      const detector = new window.BarcodeDetector({ formats: ['qr_code'] })
      const tick = async () => {
        if (!videoRef.current || !streamRef.current) return
        try {
          const codes = await detector.detect(videoRef.current)
          if (codes.length > 0) {
            const value = codes[0].rawValue
            stopScan()
            await submitToken(value)
            return
          }
        } catch {
          // transient detection error; keep scanning
        }
        rafRef.current = requestAnimationFrame(tick)
      }
      rafRef.current = requestAnimationFrame(tick)
    } catch (err: any) {
      setScanError('Could not access the camera. Check permissions and try again.')
      stopScan()
    }
  }

  useEffect(() => () => stopScan(), [])

  const reset = () => {
    setResult(null)
    setError('')
    setToken('')
    setScanError('')
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-uw-red shadow-md">
        <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">WisCard Verifier</h1>
            <p className="text-sm opacity-90">Operator scanning station</p>
          </div>
          <Link
            href="/dashboard"
            className="bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
          >
            Student View
          </Link>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-10">
        {/* Result banner */}
        {result?.success && (
          <div className="mb-8 rounded-2xl bg-green-600 p-8 text-center shadow-2xl animate-[fadeIn_0.2s_ease-out]">
            <div className="text-6xl mb-3">✅</div>
            <h2 className="text-3xl font-bold mb-4">
              {result.service_type === 'ticket' ? 'Ticket Valid' : 'Access Granted'}
            </h2>
            {result.service_type === 'ticket' ? (
              <div className="bg-white/15 rounded-xl p-6 inline-block text-left">
                <p className="text-2xl font-bold">{result.event_name}</p>
                <p className="opacity-90 mt-1">{result.venue}</p>
                {result.seat && <p className="opacity-90">{result.seat}</p>}
                <p className="opacity-90 mt-2">
                  Holder: {result.holder?.full_name} ({result.holder?.student_id})
                </p>
              </div>
            ) : (
              <div className="bg-white/15 rounded-xl p-6 inline-block text-left">
                <p className="text-2xl font-bold">{result.user?.full_name}</p>
                <p className="opacity-90 mt-1">Student ID: {result.user?.student_id}</p>
                <p className="opacity-90">NetID: {result.user?.netid}</p>
                <p className="opacity-90 mt-2 capitalize">
                  Service: {result.service_type}
                </p>
                {result.resource_name && (
                  <p className="opacity-90">Resource: {result.resource_name}</p>
                )}
              </div>
            )}
            <div>
              <button
                onClick={reset}
                className="mt-6 bg-white text-green-700 px-8 py-3 rounded-lg font-bold hover:bg-gray-100 transition-colors"
              >
                Scan Next
              </button>
            </div>
          </div>
        )}

        {error && (
          <div className="mb-8 rounded-2xl bg-red-600 p-8 text-center shadow-2xl">
            <div className="text-6xl mb-3">⛔</div>
            <h2 className="text-3xl font-bold mb-2">Access Denied</h2>
            <p className="opacity-90">{error}</p>
            <button
              onClick={reset}
              className="mt-6 bg-white text-red-700 px-8 py-3 rounded-lg font-bold hover:bg-gray-100 transition-colors"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Scanner form */}
        {!result?.success && !error && (
          <div className="bg-gray-800 rounded-2xl p-8 shadow-xl">
            <h2 className="text-lg font-semibold mb-6 text-gray-200">
              Validate a student access code
            </h2>

            <form onSubmit={handleVerify} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-3">
                  Service
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-2">
                  {SERVICES.map((s) => (
                    <button
                      key={s.value}
                      type="button"
                      onClick={() => setServiceType(s.value)}
                      className={`rounded-lg p-3 text-center text-sm font-semibold transition-colors ${
                        serviceType === s.value
                          ? 'bg-uw-red text-white'
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                    >
                      <div className="text-2xl mb-1">{s.icon}</div>
                      {s.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Resource selector for door access */}
              {serviceType === 'door' && (
                <div>
                  <label
                    htmlFor="resource"
                    className="block text-sm font-medium text-gray-400 mb-2"
                  >
                    Door / building
                  </label>
                  <select
                    id="resource"
                    value={resource}
                    onChange={(e) => setResource(e.target.value)}
                    className="w-full px-4 py-3 rounded-lg bg-gray-900 border border-gray-700 text-white text-sm focus:ring-2 focus:ring-uw-red focus:border-transparent"
                  >
                    {RESOURCES.map((r) => (
                      <option key={r.value} value={r.value}>
                        {r.label}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Camera scanner */}
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">
                  Scan with camera
                </label>
                {scanning ? (
                  <div className="relative">
                    <video
                      ref={videoRef}
                      muted
                      playsInline
                      className="w-full rounded-lg border-2 border-uw-red bg-black aspect-video object-cover"
                    />
                    <button
                      type="button"
                      onClick={stopScan}
                      className="absolute top-2 right-2 bg-black/60 hover:bg-black/80 px-3 py-1 rounded-lg text-sm"
                    >
                      Stop
                    </button>
                    <p className="text-xs text-gray-400 mt-2 text-center">
                      Point the camera at the student's QR code…
                    </p>
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={startScan}
                    className="w-full bg-gray-700 hover:bg-gray-600 py-3 rounded-lg font-semibold transition-colors"
                  >
                    📷 Open Camera Scanner
                  </button>
                )}
                {scanError && (
                  <p className="text-xs text-yellow-400 mt-2">{scanError}</p>
                )}
              </div>

              <div className="flex items-center gap-3 text-gray-500 text-xs">
                <span className="h-px flex-1 bg-gray-700" />
                OR
                <span className="h-px flex-1 bg-gray-700" />
              </div>

              <div>
                <label
                  htmlFor="token"
                  className="block text-sm font-medium text-gray-400 mb-2"
                >
                  {serviceType === 'ticket'
                    ? 'Paste the ticket code manually'
                    : 'Paste the access token manually'}
                </label>
                <input
                  id="token"
                  type="text"
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  placeholder="Paste the student's access token here"
                  className="w-full px-4 py-3 rounded-lg bg-gray-900 border border-gray-700 text-white font-mono text-sm focus:ring-2 focus:ring-uw-red focus:border-transparent"
                />
              </div>

              <button
                type="submit"
                disabled={loading || !token.trim()}
                className="w-full bg-uw-red text-white py-4 rounded-lg font-bold text-lg hover:bg-uw-red-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Verifying…' : 'Verify Access'}
              </button>
            </form>

            <p className="mt-6 text-xs text-gray-500 leading-relaxed">
              The student generates a 5-minute access code on their dashboard. Codes
              are validated against the server in real time and can be revoked by an
              administrator. Camera scanning uses the browser's native BarcodeDetector
              (Chromium); manual entry works in every browser.
            </p>
          </div>
        )}
      </main>
    </div>
  )
}
