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

export default function BlockchainCard() {
  const [walletAddress, setWalletAddress] = useState<string>('')
  const [connected, setConnected] = useState(false)
  const [loading, setLoading] = useState(false)
  const [binaryData, setBinaryData] = useState<BinaryData | null>(null)

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
      const result = await mintNFT(walletAddress)
      toast.success('NFT metadata prepared! Now mint on blockchain')

      // Display metadata
      console.log('NFT Metadata:', result.metadata)
      alert(`NFT Ready to Mint!\n\nStudent ID: ${result.metadata.student_id}\nBinary: ${result.metadata.binary_representation}\n\nNext: Use MetaMask to mint the NFT on-chain`)
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

      // Display pass data
      console.log('Apple Wallet Pass Data:', passData.pass_data)
      alert(`Apple Wallet Pass Ready!\n\nBinary Code: ${passData.binary_code}\nStudent ID: ${passData.student_id}\n\nNote: Full .pkpass file requires Apple Developer certificate`)
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
