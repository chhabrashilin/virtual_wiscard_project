/**
 * API client for Virtual Wiscard backend.
 */
import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Token management
export const getToken = () => localStorage.getItem('token')
export const setToken = (token: string) => localStorage.setItem('token', token)
export const removeToken = () => localStorage.removeItem('token')

// Auth API
export const login = async (netid: string, password: string) => {
  const formData = new FormData()
  formData.append('username', netid)
  formData.append('password', password)
  
  const response = await axios.post(`${API_BASE_URL}/api/auth/login`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  
  setToken(response.data.access_token)
  localStorage.setItem('user', JSON.stringify(response.data.user))
  return response.data
}

export const getCurrentUser = async () => {
  const response = await api.get('/api/auth/me')
  return response.data
}

// Card API
export const getMyCard = async () => {
  const response = await api.get('/api/cards/my-card')
  return response.data
}

export const generateQRCode = async () => {
  const response = await api.post('/api/cards/generate-qr')
  return response.data
}

export const getBalances = async () => {
  const response = await api.get('/api/cards/balances')
  return response.data
}

// Verifier API (operator-facing; validates a scanned/entered access token)
export const verifyAccessToken = async (
  token: string,
  serviceType: string,
  action: string = 'entry',
  resource: string | null = null
) => {
  const response = await axios.post(`${API_BASE_URL}/api/services/access`, {
    token,
    service_type: serviceType,
    action,
    resource,
  })
  return response.data
}

// Validate an event ticket at the gate (public scanner endpoint)
export const validateTicket = async (code: string) => {
  const response = await axios.post(`${API_BASE_URL}/api/tickets/validate`, { code })
  return response.data
}

// Services API
export const checkDiningBalance = async () => {
  const response = await api.post('/api/services/dining/check-balance')
  return response.data
}

export const useDiningBalance = async (amount: number) => {
  const response = await api.post('/api/services/dining/use', { amount })
  return response.data
}

export const libraryCheckout = async () => {
  const response = await api.post('/api/services/library/checkout')
  return response.data
}

export const residenceAccess = async () => {
  const response = await api.post('/api/services/residence/access')
  return response.data
}

export const checkPrintBalance = async () => {
  const response = await api.post('/api/services/print/check-balance')
  return response.data
}

export const usePrintBalance = async (amount: number) => {
  const response = await api.post('/api/services/print/use', { amount })
  return response.data
}

export const checkWiscardCash = async () => {
  const response = await api.post('/api/services/wiscard-cash/check-balance')
  return response.data
}

export const useWiscardCash = async (amount: number, vendor: string) => {
  const response = await api.post('/api/services/wiscard-cash/use', { amount, vendor })
  return response.data
}

export const getMealSwipes = async () => {
  const response = await api.get('/api/services/dining/swipes')
  return response.data
}

export const useMealSwipe = async () => {
  const response = await api.post('/api/services/dining/swipe')
  return response.data
}

export const getTransitPass = async () => {
  const response = await api.get('/api/services/transit/pass')
  return response.data
}

export const getMyPermissions = async () => {
  const response = await api.get('/api/services/access-permissions')
  return response.data
}

// Card lifecycle (lost-card freeze)
export const freezeCard = async () => {
  const response = await api.post('/api/cards/freeze')
  return response.data
}

export const unfreezeCard = async () => {
  const response = await api.post('/api/cards/unfreeze')
  return response.data
}

// Tickets
export const getMyTickets = async () => {
  const response = await api.get('/api/tickets')
  return response.data
}

// Admin: expanded management
export const grantPermission = async (data: {
  user_id: number
  resource_key: string
  resource_name: string
}) => {
  const response = await api.post('/api/admin/permissions', data)
  return response.data
}

export const revokePermission = async (data: {
  user_id: number
  resource_key: string
  resource_name: string
}) => {
  const response = await api.post('/api/admin/permissions/revoke', data)
  return response.data
}

export const setMealSwipes = async (data: {
  user_id: number
  plan_name: string
  swipes_remaining: number
}) => {
  const response = await api.post('/api/admin/meal-swipes', data)
  return response.data
}

export const setTransitPass = async (data: {
  user_id: number
  status: string
  semester?: string
  valid_until?: string | null
}) => {
  const response = await api.post('/api/admin/transit', data)
  return response.data
}

export const issueTicket = async (data: {
  user_id: number
  event_name: string
  event_date?: string | null
  venue?: string
  seat?: string | null
}) => {
  const response = await api.post('/api/admin/tickets', data)
  return response.data
}

// Admin API
export const getAllUsers = async () => {
  const response = await api.get('/api/admin/users')
  return response.data
}

export const createUser = async (userData: any) => {
  const response = await api.post('/api/admin/users', userData)
  return response.data
}

export const toggleUserActive = async (userId: number) => {
  const response = await api.patch(`/api/admin/users/${userId}/toggle-active`)
  return response.data
}

export const updateBalance = async (balanceData: any) => {
  const response = await api.post('/api/admin/balances', balanceData)
  return response.data
}

export const getStats = async () => {
  const response = await api.get('/api/admin/stats')
  return response.data
}

// Transaction History API
export const getTransactionHistory = async (limit: number = 50) => {
  const response = await api.get(`/api/cards/transaction-history?limit=${limit}`)
  return response.data
}

// Blockchain API
export const getBinaryConversion = async () => {
  const response = await api.post('/api/blockchain/student-id-to-binary')
  return response.data
}

export const mintNFT = async (walletAddress: string) => {
  const response = await api.post('/api/blockchain/mint-nft', { wallet_address: walletAddress })
  return response.data
}

export const verifyNFT = async (walletAddress: string) => {
  const response = await api.get(`/api/blockchain/verify-nft/${walletAddress}`)
  return response.data
}

// Apple Wallet API
export const getAppleWalletData = async (nftTokenId: string | null = null) => {
  const response = await api.post('/api/wallet/generate-pkpass-data', {
    nft_token_id: nftTokenId
  })
  return response.data
}

export const getBarcodeData = async () => {
  const response = await api.get('/api/wallet/barcode-data')
  return response.data
}

