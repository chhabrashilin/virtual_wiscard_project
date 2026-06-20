'use client'

import { useEffect, useState } from 'react'
import { QRCodeSVG } from 'qrcode.react'
import { getMyTickets } from '@/lib/api'

interface Ticket {
  id: number
  code: string
  event_name: string
  event_date: string | null
  venue: string
  seat: string | null
  status: string
  used_at: string | null
}

export default function TicketsCard() {
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    load()
  }, [])

  const load = async () => {
    try {
      const data = await getMyTickets()
      setTickets(data.tickets)
    } catch {
      /* ignore */
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (s: string | null) =>
    s
      ? new Date(s).toLocaleString('en-US', {
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        })
      : 'TBD'

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
      <h3 className="text-lg font-bold text-gray-800 mb-4">🎟️ Event Tickets</h3>

      {loading && <p className="text-sm text-gray-500">Loading…</p>}

      {!loading && tickets.length === 0 && (
        <p className="text-sm text-gray-500">No tickets yet. Athletic & event tickets appear here.</p>
      )}

      <div className="space-y-4">
        {tickets.map((t) => {
          const used = t.status !== 'valid'
          return (
            <div
              key={t.id}
              className={`flex items-center gap-4 rounded-lg border p-4 ${
                used ? 'opacity-60 border-gray-200' : 'border-uw-red/30 bg-uw-red/5'
              }`}
            >
              <div className="bg-white p-2 rounded-lg border border-gray-200">
                <QRCodeSVG value={t.code} size={84} />
              </div>
              <div className="flex-1">
                <p className="font-bold text-gray-800">{t.event_name}</p>
                <p className="text-sm text-gray-600">{t.venue}</p>
                {t.seat && <p className="text-xs text-gray-500">{t.seat}</p>}
                <p className="text-xs text-gray-500 mt-1">{formatDate(t.event_date)}</p>
                <span
                  className={`inline-block mt-2 text-xs px-2 py-0.5 rounded-full font-semibold ${
                    used ? 'bg-gray-200 text-gray-600' : 'bg-green-100 text-green-800'
                  }`}
                >
                  {t.status.toUpperCase()}
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
