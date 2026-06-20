'use client'

import { useState } from 'react'
import { mintNFT, getBinaryConversion, getAppleWalletData } from '@/lib/api'
import toast from 'react-hot-toast'

interface BinaryData {
  student_id: string
  binary: string
  binary_length: number
  barcode_type: string
}

interface ResultPanel {
  title: string
  rows: { label: string; value: string }[]
  note?: string
}

export default function BlockchainCard() {
  const [walletAddress, setWalletAddress] = useState<string>('')
  const [connected, setConnected] = useState(false)
  const [loading, setLoading] = useState(false)
  const [binaryData, setBinaryData] = useState<BinaryData | null>(null)
  const [result, setResult] = useState<ResultPanel | null>(null)

  const connectWallet = async () => {
    if (typeof window.ethereum === 'undefined') {
      toast.error('MetaMask not installed! Please install MetaMask to continue.')
      return
    }

    try {
      setLoading(true)
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts'
      })

      if (accounts.length > 0) {
        setWalletAddress(accounts[0])
        setConnected(true)
        toast.success('Wallet connected successfully!')

        // Load binary conversion
        const binary = await getBinaryConversion()
        setBinaryData(binary)
      }
    } catch (error: any) {
      toast.error(error.message || 'Failed to connect wallet')
    } finally {
      setLoading(false)
    }
  }

  const handleMintNFT = async () => {
    if (!connected || !walletAddress) {
      toast.error('Please connect your wallet first')
      return
    }

    try {
      setLoading(true)
      const res = await mintNFT(walletAddress)
      toast.success('NFT metadata prepared!')
      setResult({
        title: '🎨 Soulbound NFT — Ready to Mint',
        rows: [
          { label: 'Student', value: res.metadata.student_name },
          { label: 'Student ID', value: res.metadata.student_id },
          { label: 'Binary', value: res.metadata.binary_representation },
          { label: 'Network', value: res.metadata.network },
          { label: 'Type', value: res.metadata.token_type },
          { label: 'Wallet', value: res.metadata.wallet_address },
        ],
        note: 'Next: confirm the transaction in MetaMask to mint on-chain.',
      })
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to prepare NFT')
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadAppleWallet = async () => {
    try {
      setLoading(true)
      const passData = await getAppleWalletData()
      toast.success('Apple Wallet pass data generated!')

      // Offer the pass.json for download so it can be packaged into a .pkpass
      const blob = new Blob([JSON.stringify(passData.pass_data, null, 2)], {
        type: 'application/json',
      })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `wiscard-pass-${passData.student_id}.json`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)

      setResult({
        title: '🍎 Apple Wallet Pass',
        rows: [
          { label: 'Student ID', value: passData.student_id },
          { label: 'Binary code', value: passData.binary_code },
          { label: 'Barcode', value: 'PDF417 (binary-encoded)' },
          { label: 'Downloaded', value: `wiscard-pass-${passData.student_id}.json` },
        ],
        note: 'pass.json downloaded. Full .pkpass packaging requires an Apple Developer certificate.',
      })
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to generate Apple Wallet pass')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-gradient-to-br from-purple-600 to-blue-600 rounded-xl shadow-lg p-6 text-white">
      <h3 className="text-xl font-bold mb-4">🔗 Blockchain & Apple Wallet</h3>

      {!connected ? (
        <div className="text-center py-6">
          <p className="mb-4 text-sm opacity-90">
            Connect your wallet to mint a Soulbound NFT and generate Apple Wallet pass
          </p>
          <button
            onClick={connectWallet}
            disabled={loading}
            className="bg-white text-purple-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors disabled:opacity-50"
          >
            {loading ? 'Connecting...' : '🦊 Connect MetaMask'}
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="bg-white/10 rounded-lg p-4 backdrop-blur">
            <p className="text-xs opacity-75 mb-1">Connected Wallet</p>
            <p className="font-mono text-sm break-all">
              {walletAddress.slice(0, 6)}...{walletAddress.slice(-4)}
            </p>
          </div>

          {binaryData && (
            <div className="bg-white/10 rounded-lg p-4 backdrop-blur">
              <p className="text-xs opacity-75 mb-1">Student ID Binary</p>
              <p className="font-mono text-sm break-all mb-2">{binaryData.binary}</p>
              <p className="text-xs opacity-75">
                {binaryData.binary_length} bits | {binaryData.barcode_type} format
              </p>
            </div>
          )}

          <div className="grid grid-cols-1 gap-3">
            <button
              onClick={handleMintNFT}
              disabled={loading}
              className="bg-white text-purple-600 px-4 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors disabled:opacity-50"
            >
              {loading ? 'Processing...' : '🎨 Mint Soulbound NFT'}
            </button>

            <button
              onClick={handleDownloadAppleWallet}
              disabled={loading}
              className="bg-white/20 backdrop-blur px-4 py-3 rounded-lg font-semibold hover:bg-white/30 transition-colors disabled:opacity-50"
            >
              {loading ? 'Generating...' : '🍎 Generate Apple Wallet Pass'}
            </button>
          </div>

          {result && (
            <div className="bg-white text-gray-800 rounded-lg p-4 shadow-lg">
              <div className="flex items-start justify-between mb-3">
                <p className="font-bold text-sm">{result.title}</p>
                <button
                  onClick={() => setResult(null)}
                  className="text-gray-400 hover:text-gray-600 text-lg leading-none"
                  aria-label="Dismiss"
                >
                  ×
                </button>
              </div>
              <div className="space-y-2">
                {result.rows.map((row) => (
                  <div key={row.label} className="text-xs">
                    <span className="text-gray-500">{row.label}</span>
                    <p className="font-mono break-all text-gray-900">{row.value}</p>
                  </div>
                ))}
              </div>
              {result.note && (
                <p className="text-xs text-purple-700 mt-3 border-t pt-2">
                  {result.note}
                </p>
              )}
            </div>
          )}

          <div className="bg-white/10 rounded-lg p-4 backdrop-blur text-xs space-y-2">
            <p className="font-semibold">✨ Features:</p>
            <ul className="space-y-1 opacity-90">
              <li>• Non-transferable NFT (Soulbound to wallet)</li>
              <li>• PDF417 barcode from binary encoding</li>
              <li>• Apple Wallet integration</li>
              <li>• On-chain verification</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}
