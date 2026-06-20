'use client'

import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import {
  getAllUsers,
  issueTicket,
  grantPermission,
  revokePermission,
  setMealSwipes,
  setTransitPass,
} from '@/lib/api'

interface User {
  id: number
  netid: string
  full_name: string
}

const RESOURCE_PRESETS = [
  { key: 'recwell', name: 'RecWell (Nick & Bakke)' },
  { key: 'sellery_hall', name: 'Sellery Residence Hall' },
  { key: 'witte_hall', name: 'Witte Residence Hall' },
  { key: 'chadbourne_hall', name: 'Chadbourne Residence Hall' },
  { key: 'chem_lab', name: 'Chemistry Lab 301' },
]

export default function AdminCampusServices() {
  const [users, setUsers] = useState<User[]>([])
  const [userId, setUserId] = useState<number | ''>('')

  // ticket form
  const [eventName, setEventName] = useState('')
  const [venue, setVenue] = useState('')
  const [seat, setSeat] = useState('')

  // access form
  const [resourceKey, setResourceKey] = useState('recwell')

  // meal swipes
  const [planName, setPlanName] = useState('Flex')
  const [swipes, setSwipes] = useState('')

  // transit
  const [transitStatus, setTransitStatus] = useState('active')
  const [semester, setSemester] = useState('Fall 2026')

  useEffect(() => {
    getAllUsers()
      .then((d) => setUsers(d.users))
      .catch(() => {})
  }, [])

  const requireUser = (): number | null => {
    if (!userId) {
      toast.error('Select a user first')
      return null
    }
    return Number(userId)
  }

  const handleIssueTicket = async () => {
    const uid = requireUser()
    if (uid === null) return
    if (!eventName) {
      toast.error('Event name is required')
      return
    }
    try {
      await issueTicket({ user_id: uid, event_name: eventName, venue, seat: seat || null })
      toast.success('Ticket issued')
      setEventName('')
      setVenue('')
      setSeat('')
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'Failed to issue ticket')
    }
  }

  const resourceName = () =>
    RESOURCE_PRESETS.find((r) => r.key === resourceKey)?.name || resourceKey

  const handleGrant = async () => {
    const uid = requireUser()
    if (uid === null) return
    try {
      await grantPermission({ user_id: uid, resource_key: resourceKey, resource_name: resourceName() })
      toast.success('Access granted')
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'Failed to grant access')
    }
  }

  const handleRevoke = async () => {
    const uid = requireUser()
    if (uid === null) return
    try {
      await revokePermission({ user_id: uid, resource_key: resourceKey, resource_name: resourceName() })
      toast.success('Access revoked')
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'Failed to revoke access')
    }
  }

  const handleMealSwipes = async () => {
    const uid = requireUser()
    if (uid === null) return
    const value = parseInt(swipes, 10)
    if (Number.isNaN(value) || value < 0) {
      toast.error('Enter a valid swipe count')
      return
    }
    try {
      await setMealSwipes({ user_id: uid, plan_name: planName, swipes_remaining: value })
      toast.success('Meal plan updated')
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'Failed to update meal plan')
    }
  }

  const handleTransit = async () => {
    const uid = requireUser()
    if (uid === null) return
    try {
      await setTransitPass({ user_id: uid, status: transitStatus, semester })
      toast.success('Transit pass updated')
    } catch (e: any) {
      toast.error(e.response?.data?.detail || 'Failed to update transit pass')
    }
  }

  const inputCls = 'px-3 py-2 border border-gray-300 rounded-lg text-sm'

  return (
    <div className="bg-white rounded-lg shadow border border-gray-200 p-6 space-y-6">
      <h3 className="text-xl font-bold text-gray-800">Campus Services Management</h3>

      {/* Shared user selector */}
      <div>
        <label className="block text-sm font-medium text-gray-600 mb-1">Student</label>
        <select
          value={userId}
          onChange={(e) => setUserId(e.target.value ? Number(e.target.value) : '')}
          className={`${inputCls} w-full md:w-1/2`}
        >
          <option value="">Select a student…</option>
          {users.map((u) => (
            <option key={u.id} value={u.id}>
              {u.netid} — {u.full_name}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Issue ticket */}
        <div className="border border-gray-200 rounded-lg p-4">
          <h4 className="font-semibold text-gray-800 mb-3">🎟️ Issue Event Ticket</h4>
          <div className="space-y-2">
            <input className={`${inputCls} w-full`} placeholder="Event name" value={eventName} onChange={(e) => setEventName(e.target.value)} />
            <input className={`${inputCls} w-full`} placeholder="Venue" value={venue} onChange={(e) => setVenue(e.target.value)} />
            <input className={`${inputCls} w-full`} placeholder="Seat (optional)" value={seat} onChange={(e) => setSeat(e.target.value)} />
            <button onClick={handleIssueTicket} className="bg-uw-red text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-uw-red-dark">
              Issue Ticket
            </button>
          </div>
        </div>

        {/* Building access */}
        <div className="border border-gray-200 rounded-lg p-4">
          <h4 className="font-semibold text-gray-800 mb-3">🚪 Building / Door Access</h4>
          <div className="space-y-2">
            <select className={`${inputCls} w-full`} value={resourceKey} onChange={(e) => setResourceKey(e.target.value)}>
              {RESOURCE_PRESETS.map((r) => (
                <option key={r.key} value={r.key}>{r.name}</option>
              ))}
            </select>
            <div className="flex gap-2">
              <button onClick={handleGrant} className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-green-700">
                Grant
              </button>
              <button onClick={handleRevoke} className="bg-red-100 text-red-700 px-4 py-2 rounded-lg text-sm font-semibold hover:bg-red-200">
                Revoke
              </button>
            </div>
          </div>
        </div>

        {/* Meal swipes */}
        <div className="border border-gray-200 rounded-lg p-4">
          <h4 className="font-semibold text-gray-800 mb-3">🍽️ Meal Plan</h4>
          <div className="space-y-2">
            <input className={`${inputCls} w-full`} placeholder="Plan name" value={planName} onChange={(e) => setPlanName(e.target.value)} />
            <input className={`${inputCls} w-full`} type="number" min="0" placeholder="Swipes remaining" value={swipes} onChange={(e) => setSwipes(e.target.value)} />
            <button onClick={handleMealSwipes} className="bg-uw-red text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-uw-red-dark">
              Update Meal Plan
            </button>
          </div>
        </div>

        {/* Transit */}
        <div className="border border-gray-200 rounded-lg p-4">
          <h4 className="font-semibold text-gray-800 mb-3">🚌 Transit Pass</h4>
          <div className="space-y-2">
            <select className={`${inputCls} w-full`} value={transitStatus} onChange={(e) => setTransitStatus(e.target.value)}>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
            <input className={`${inputCls} w-full`} placeholder="Semester" value={semester} onChange={(e) => setSemester(e.target.value)} />
            <button onClick={handleTransit} className="bg-uw-red text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-uw-red-dark">
              Update Transit Pass
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
