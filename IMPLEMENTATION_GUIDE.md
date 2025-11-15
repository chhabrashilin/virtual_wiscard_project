# Virtual WisCard 2.0 - Implementation Guide

## 🚀 New Features Implemented

### Backend Enhancements

1. **Security Improvements**
   - ✅ Environment variable configuration (.env support)
   - ✅ SECRET_KEY now loaded from environment variables
   - ✅ Input validation with Pydantic validators
   - ✅ Transaction rollback on errors
   - ✅ Expired card checking in authentication
   - ✅ Amount validation (prevents negative balances)

2. **Blockchain Integration**
   - ✅ Student ID to Binary conversion endpoint
   - ✅ NFT minting preparation endpoint
   - ✅ Wallet verification system
   - ✅ Solidity smart contract (WisCardNFT.sol)
   - ✅ Soulbound (non-transferable) NFT support

3. **Apple Wallet Integration**
   - ✅ pass.json generation for .pkpass files
   - ✅ PDF417 barcode data from binary encoding
   - ✅ Apple Wallet pass metadata endpoint

4. **Database Optimizations**
   - ✅ Added indexes on foreign keys
   - ✅ Composite indexes for common query patterns
   - ✅ AccessToken relationship to User model
   - ✅ location field added to AccessLog

5. **New API Endpoints**
   - `/api/blockchain/student-id-to-binary` - Convert student ID to binary
   - `/api/blockchain/mint-nft` - Prepare NFT metadata
   - `/api/blockchain/verify-nft/{wallet}` - Verify NFT ownership
   - `/api/wallet/generate-pkpass-data` - Generate Apple Wallet pass
   - `/api/wallet/barcode-data` - Get barcode data
   - `/api/cards/transaction-history` - Get user transaction history

### Frontend Enhancements

1. **New Components**
   - ✅ `BlockchainCard` - Web3 wallet connection and NFT minting
   - ✅ `TransactionHistory` - Display recent activity
   - ✅ QR Code countdown timer with progress bar
   - ✅ Toast notifications for user feedback

2. **UX Improvements**
   - ✅ Real-time countdown timer for QR codes
   - ✅ Color-coded progress bars (green → yellow → red)
   - ✅ Auto-clear expired QR codes
   - ✅ MetaMask wallet integration
   - ✅ Binary conversion display

3. **New Dependencies**
   - `ethers` v6.9.0 - Ethereum library
   - `jsbarcode` v3.11.5 - Barcode generation
   - `react-hot-toast` v2.4.1 - Toast notifications
   - `python-dotenv` - Environment variables
   - `web3` v6.11.3 - Web3 integration
   - `barcode` v0.15.1 - Python barcode generation

## 📋 Setup Instructions

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and set your SECRET_KEY:
# SECRET_KEY=$(openssl rand -hex 32)

# Initialize database
python init_db.py

# Run the backend
uvicorn app.main:app --reload
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

### 3. Docker Setup (Recommended)

```bash
# From project root
docker-compose down
docker-compose up --build
```

## 🔐 Environment Variables

### Backend (.env)

```env
# Security
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
JWT_EXPIRATION_MINUTES=30

# Database
DATABASE_URL=sqlite:///./data/virtual_wiscard.db

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Blockchain (Optional)
CONTRACT_ADDRESS=0x... # Your deployed smart contract address
PROVIDER_URL=https://polygon-mumbai.g.alchemy.com/v2/your-api-key
CHAIN_ID=80001

# Apple Wallet (Optional)
APPLE_TEAM_ID=YOUR_TEAM_ID
APPLE_PASS_TYPE_ID=pass.edu.wisc.wiscard
APPLE_CERT_PATH=/path/to/cert.p12
```

## 🎨 Smart Contract Deployment

### Using Hardhat/Remix

1. **Install Dependencies**
```bash
npm install --save-dev hardhat @openzeppelin/contracts
```

2. **Deploy Contract**
```javascript
// scripts/deploy.js
const { ethers } = require("hardhat");

async function main() {
  const WisCardNFT = await ethers.getContractFactory("WisCardNFT");
  const wiscard = await WisCardNFT.deploy();
  await wiscard.deployed();
  console.log("WisCardNFT deployed to:", wiscard.address);
}

main();
```

3. **Update Backend .env**
```env
CONTRACT_ADDRESS=0x... # Address from deployment
```

## 🍎 Apple Wallet Setup (Advanced)

### Prerequisites
- Apple Developer Account ($99/year)
- Pass Type ID registered in Apple Developer Portal
- Apple certificate (.p12 file)

### Steps

1. **Register Pass Type ID**
   - Go to developer.apple.com
   - Certificates, Identifiers & Profiles
   - Create Pass Type ID: `pass.edu.wisc.wiscard`

2. **Generate Certificate**
   ```bash
   # Create CSR
   openssl req -new -key private.key -out request.csr

   # Download certificate from Apple
   # Export as .p12 file
   ```

3. **Update Backend .env**
   ```env
   APPLE_TEAM_ID=ABC123XYZ
   APPLE_PASS_TYPE_ID=pass.edu.wisc.wiscard
   APPLE_CERT_PATH=/path/to/cert.p12
   ```

## 🧪 Testing the New Features

### 1. Test Binary Conversion

```bash
# Login first
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: multipart/form-data" \
  -F "username=jdoe" \
  -F "password=password123"

# Get binary conversion
curl -X POST http://localhost:8000/api/blockchain/student-id-to-binary \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Test NFT Minting

```bash
curl -X POST http://localhost:8000/api/blockchain/mint-nft \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"wallet_address": "0x..."}'
```

### 3. Test Apple Wallet Pass

```bash
curl -X POST http://localhost:8000/api/wallet/generate-pkpass-data \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nft_token_id": "1"}'
```

### 4. Test Transaction History

```bash
curl http://localhost:8000/api/cards/transaction-history \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🎯 Feature Walkthrough

### Using Blockchain Features

1. **Open Dashboard**: http://localhost:3000/dashboard
2. **Connect Wallet**: Click "Connect MetaMask" in Blockchain card
3. **View Binary**: See student ID converted to binary
4. **Mint NFT**: Click "Mint Soulbound NFT" (requires MetaMask)
5. **Generate Pass**: Click "Generate Apple Wallet Pass"

### Using QR Code Timer

1. **Generate QR Code**: Click "Generate QR Code"
2. **Watch Countdown**: 5-minute timer with color-coded progress
3. **Auto-Refresh**: Code expires and prompts for new generation

### Viewing Transaction History

1. **Dashboard**: Scroll to "Recent Activity" section
2. **View Logs**: See all dining, library, residence access
3. **Filter**: Transactions show service type, time, location

## 🛠️ Troubleshooting

### Issue: SECRET_KEY Warning

**Solution**: Generate a new secret key
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Add to `.env`:
```env
SECRET_KEY=generated-key-here
```

### Issue: MetaMask Not Detected

**Solution**: Install MetaMask browser extension
- Chrome: https://metamask.io/download/
- Firefox: https://addons.mozilla.org/en-US/firefox/addon/ether-metamask/

### Issue: Docker Build Fails

**Solution**: Clear Docker cache
```bash
docker-compose down -v
docker system prune -a
docker-compose up --build
```

### Issue: Database Migration Needed

**Solution**: Delete old database and reinitialize
```bash
cd backend
rm -rf data/virtual_wiscard.db
python init_db.py
```

## 📊 Database Schema Changes

### New Fields
- `AccessLog.location` (String, nullable)
- `AccessLog.created_at` (renamed from `timestamp`)

### New Indexes
- `idx_user_created` on `(user_id, created_at)`
- `idx_service_created` on `(service_type, created_at)`
- Foreign key indexes on `user_id` in all tables

## 🚀 Production Deployment

### Environment Variables (Production)

```env
# Generate a strong secret key
SECRET_KEY=$(openssl rand -hex 32)

# Use PostgreSQL instead of SQLite
DATABASE_URL=postgresql://user:pass@localhost:5432/wiscard

# Restrict CORS
CORS_ORIGINS=https://wiscard.wisc.edu

# Set environment
ENVIRONMENT=production
```

### Docker Production

```yaml
# docker-compose.prod.yml
services:
  backend:
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    # Remove --reload flag
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - ENVIRONMENT=production
```

## 🎓 Demo Script for Hackathon

### 1. Introduction (30 seconds)
*"Traditional student IDs are outdated. We've built a blockchain-verified digital WisCard that lives in your Apple Wallet."*

### 2. Live Demo (2 minutes)
1. **Login**: `jdoe` / `password123`
2. **Show Dashboard**: Virtual card, balances
3. **Generate QR Code**: Demonstrate countdown timer
4. **Connect MetaMask**: Show wallet integration
5. **View Binary**: Student ID → Binary conversion
6. **Mint NFT**: Prepare soulbound NFT
7. **Generate Pass**: Apple Wallet integration
8. **Transaction History**: Show activity logs

### 3. Technical Highlights (1 minute)
- Full-stack: React + FastAPI + Solidity
- Security: JWT auth, input validation, environment variables
- Blockchain: Soulbound NFTs prevent ID sharing
- Innovation: Binary encoding, PDF417 barcodes
- UX: Real-time timers, toast notifications

### 4. Impact (30 seconds)
*"Prevents ID sharing, reduces plastic waste, integrates with existing campus systems, and provides a foundation for blockchain-verified credentials."*

## 📝 Test Accounts

```
Student Accounts:
- jdoe / password123
- jsmith / password123
- bwilliams / password123

Admin Account:
- admin / admin123
```

## 🔗 API Documentation

Access interactive API docs at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## 📦 Project Structure

```
virtual_wiscard_project/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   ├── cards.py
│   │   │   ├── services.py
│   │   │   ├── admin.py
│   │   │   ├── blockchain.py  # NEW
│   │   │   └── wallet.py      # NEW
│   │   ├── models.py          # UPDATED
│   │   ├── auth.py            # UPDATED
│   │   └── main.py            # UPDATED
│   ├── .env                   # NEW
│   └── requirements.txt       # UPDATED
├── frontend/
│   ├── components/
│   │   ├── BlockchainCard.tsx       # NEW
│   │   ├── TransactionHistory.tsx   # NEW
│   │   ├── QRCodeDisplay.tsx        # UPDATED
│   │   └── ...
│   ├── lib/api.ts            # UPDATED
│   └── package.json          # UPDATED
├── contracts/
│   └── WisCardNFT.sol        # NEW
└── IMPLEMENTATION_GUIDE.md   # THIS FILE
```

## ✅ Implementation Checklist

- [x] Security fixes (env variables, validation)
- [x] Blockchain integration (NFT, binary conversion)
- [x] Apple Wallet pass generation
- [x] Transaction history endpoint + UI
- [x] QR code countdown timer
- [x] Database optimizations (indexes)
- [x] Web3 wallet integration
- [x] Toast notifications
- [x] Smart contract (Solidity)
- [x] Error handling improvements

## 🎉 Ready for Demo!

Your Virtual WisCard 2.0 is now hackathon-ready with:
- ✨ Blockchain/NFT integration
- 🍎 Apple Wallet support
- 📊 Transaction history
- ⏱️ Real-time QR timers
- 🔐 Enhanced security
- 🎨 Modern UI/UX
