'use client'

import { useEffect, useState } from 'react'
import { getTransitPass, getMyPermissions } from '@/lib/api'

interface Permission {
  resource_key: string
  resource_name: string
}

interface Transit {
  status: string
  semester: string
  valid_until: string | null
}

export default function CampusAccessCard() {
  const [transit, setTransit] = useState<Transit | null>(null)
  const [permissions, setPermissions] = useState<Permission[]>([])

  useEffect(() => {
    load()
  }, [])

  const load = async () => {
    try {
      const [t, p] = await Promise.all([getTransitPass(), getMyPermissions()])
      setTransit(t)
      setPermissions(p.permissions)
    } catch {
      /* ignore */
    }
  }

  const formatDate = (s: string | null) =>
    s ? new Date(s).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : ''

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
      <h3 className="text-lg font-bold text-gray-800 mb-4">🚪 Access & Transit</h3>

      {/* Transit */}
      <div className="mb-5">
        <div className="flex items-center justify-between">
          <span className="text-sm font-semibold text-gray-700">🚌 Madison Metro Bus Pass</span>
          <span
            className={`text-xs px-2 py-1 rounded-full font-semibold ${
              transit?.status === 'active'
                ? 'bg-green-100 text-green-800'
                : 'bg-gray-200 text-gray-600'
            }`}
          >
            {transit?.status === 'active' ? 'Active' : 'Inactive'}
          </span>
        </div>
        {transit?.status === 'active' && (
          <p className="text-xs text-gray-500 mt-1">
            {transit.semester} · valid through {formatDate(transit.valid_until)}
          </p>
        )}
      </div>

      {/* Door permissions */}
      <div>
        <p className="text-sm font-semibold text-gray-700 mb-2">Building &amp; door access</p>
        {permissions.length === 0 ? (
          <p className="text-xs text-gray-500">No building access granted</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {permissions.map((p) => (
              <span
                key={p.resource_key}
                className="text-xs bg-uw-red/10 text-uw-red px-3 py-1 rounded-full font-medium"
              >
                {p.resource_name}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
