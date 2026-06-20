'use client'

import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { getMealSwipes, useMealSwipe } from '@/lib/api'

export default function MealSwipesCard() {
  const [planName, setPlanName] = useState<string | null>(null)
  const [swipes, setSwipes] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    load()
  }, [])

  const load = async () => {
    try {
      const data = await getMealSwipes()
      setPlanName(data.plan_name)
      setSwipes(data.swipes_remaining)
    } catch {
      /* ignore */
    }
  }

  const handleSwipe = async () => {
    setLoading(true)
    try {
      const data = await useMealSwipe()
      setSwipes(data.swipes_remaining)
      toast.success('Meal swipe used. Enjoy!')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Could not use a swipe')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-800">🍽️ Meal Plan</h3>
        {planName && (
          <span className="text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded-full font-semibold">
            {planName}
          </span>
        )}
      </div>

      <p className="text-4xl font-bold text-gray-800 mb-1">
        {swipes !== null ? swipes : '—'}
      </p>
      <p className="text-xs text-gray-500 mb-5">Meal swipes remaining</p>

      <button
        onClick={handleSwipe}
        disabled={loading || swipes === 0}
        className="w-full bg-uw-red text-white py-2.5 rounded-lg font-semibold hover:bg-uw-red-dark transition-colors disabled:opacity-50"
      >
        {loading ? 'Processing…' : swipes === 0 ? 'No swipes left' : 'Use a Swipe'}
      </button>
    </div>
  )
}
