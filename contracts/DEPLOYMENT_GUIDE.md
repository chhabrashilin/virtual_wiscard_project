# WisCardNFT Smart Contract Deployment Guide

## Prerequisites

- MetaMask wallet with testnet ETH
- Node.js and npm installed
- Hardhat or Remix IDE

## Option 1: Deploy with Remix (Easiest)

### Step 1: Open Remix
Visit: https://remix.ethereum.org

### Step 2: Create Contract File
1. Create new file: `WisCardNFT.sol`
2. Copy contents from `contracts/WisCardNFT.sol`

### Step 3: Install OpenZeppelin
1. In Remix, go to Plugin Manager
2. Activate "Solidity Compiler"
3. Activate "Deploy & Run Transactions"
4. In the file explorer, OpenZeppelin imports will auto-resolve

### Step 4: Compile
1. Go to "Solidity Compiler" tab
2. Select compiler version: 0.8.0 or higher
3. Click "Compile WisCardNFT.sol"
4. Check for no errors

### Step 5: Deploy
1. Go to "Deploy & Run Transactions" tab
2. Select Environment: "Injected Provider - MetaMask"
3. MetaMask will pop up - select Polygon Mumbai testnet
4. Select Contract: "WisCardNFT"
5. Click "Deploy"
6. Confirm in MetaMask
7. **Copy deployed contract address**

### Step 6: Update Backend
```bash
# Update backend/.env
CONTRACT_ADDRESS=0x... # Your deployed address
PROVIDER_URL=https://polygon-mumbai.g.alchemy.com/v2/your-key
CHAIN_ID=80001
```

## Option 2: Deploy with Hardhat

### Step 1: Initialize Hardhat Project

```bash
mkdir hardhat-wiscard
cd hardhat-wiscard
npm init -y
npm install --save-dev hardhat @nomiclabs/hardhat-ethers ethers
npm install @openzeppelin/contracts
npx hardhat
```

Select: "Create a JavaScript project"

### Step 2: Copy Contract

```bash
cp ../contracts/WisCardNFT.sol contracts/
```

### Step 3: Configure Network

Edit `hardhat.config.js`:

```javascript
require("@nomiclabs/hardhat-ethers");

module.exports = {
  solidity: "0.8.0",
  networks: {
    mumbai: {
      url: "https://polygon-mumbai.g.alchemy.com/v2/YOUR_ALCHEMY_KEY",
      accounts: ["YOUR_PRIVATE_KEY"] // From MetaMask
    }
  }
};
```

### Step 4: Create Deployment Script

Create `scripts/deploy.js`:

```javascript
async function main() {
  const WisCardNFT = await ethers.getContractFactory("WisCardNFT");
  console.log("Deploying WisCardNFT...");

  const wiscard = await WisCardNFT.deploy();
  await wiscard.deployed();

  console.log("WisCardNFT deployed to:", wiscard.address);
  console.log("Save this address to backend/.env");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
```

### Step 5: Deploy

```bash
npx hardhat run scripts/deploy.js --network mumbai
```

### Step 6: Verify on PolygonScan

```bash
npx hardhat verify --network mumbai DEPLOYED_CONTRACT_ADDRESS
```

## Testing the Contract

### Test Minting (Remix)

1. In "Deploy & Run Transactions", find your deployed contract
2. Expand "mintWisCard" function
3. Input:
   - `_studentName`: "John Doe"
   - `_studentId`: 1234567
   - `_binaryRepresentation`: "100101101011010000111"
   - `_issueDate`: "2024-01-15"
   - `_expiryDate`: "2025-01-15"
   - `_barcodeData`: 0x (empty bytes for now)
4. Click "transact"
5. Confirm in MetaMask

### Test Minting (Hardhat)

Create `scripts/mint.js`:

```javascript
async function main() {
  const contractAddress = "YOUR_DEPLOYED_ADDRESS";
  const WisCardNFT = await ethers.getContractFactory("WisCardNFT");
  const wiscard = await WisCardNFT.attach(contractAddress);

  const binary = parseInt("1234567").toString(2);

  const tx = await wiscard.mintWisCard(
    "John Doe",
    1234567,
    binary,
    "2024-01-15",
    "2025-01-15",
    ethers.utils.toUtf8Bytes(binary)
  );

  await tx.wait();
  console.log("NFT minted! Transaction:", tx.hash);
}

main();
```

Run:
```bash
npx hardhat run scripts/mint.js --network mumbai
```

## Verify NFT Ownership

```javascript
// In Remix or Hardhat console
const tokenId = 0; // First minted token
const studentData = await wiscard.getStudentData(tokenId);
console.log(studentData);

const isOwner = await wiscard.verifyOwnership(tokenId, "0xYourWalletAddress");
console.log("Owns NFT:", isOwner);
```

## Common Issues

### Issue: "Insufficient funds for intrinsic transaction cost"

**Solution**: Get testnet MATIC from faucet
- https://faucet.polygon.technology/
- Select Mumbai
- Enter your wallet address
- Wait 1-2 minutes

### Issue: "Contract creation code storage out of gas"

**Solution**: Increase gas limit in deployment
```javascript
const wiscard = await WisCardNFT.deploy({ gasLimit: 5000000 });
```

### Issue: "Transaction underpriced"

**Solution**: Increase gas price
```javascript
const wiscard = await WisCardNFT.deploy({
  gasPrice: ethers.utils.parseUnits("50", "gwei")
});
```

## Production Deployment (Mainnet)

### ⚠️ WARNING: Real Money Required

1. **Get Real MATIC**: Use an exchange (Coinbase, Binance)
2. **Audit Contract**: Consider professional audit
3. **Test Thoroughly**: Deploy to testnet first
4. **Update hardhat.config.js**:

```javascript
networks: {
  polygon: {
    url: "https://polygon-rpc.com",
    accounts: ["YOUR_PRIVATE_KEY"],
    chainId: 137
  }
}
```

5. **Deploy**:
```bash
npx hardhat run scripts/deploy.js --network polygon
```

## Integration with Frontend

Once deployed, update `frontend/components/BlockchainCard.tsx`:

```typescript
// Add contract ABI (from Remix or Hardhat artifacts)
const CONTRACT_ABI = [ /* ABI array here */ ];

// In mintNFT function
const contract = new ethers.Contract(
  process.env.NEXT_PUBLIC_CONTRACT_ADDRESS,
  CONTRACT_ABI,
  signer
);

const tx = await contract.mintWisCard(
  studentName,
  studentId,
  binary,
  issueDate,
  expiryDate,
  ethers.utils.toUtf8Bytes(binary)
);

await tx.wait();
```

## Contract Features

### Soulbound (Non-Transferable)
```solidity
// Transfer functions are overridden to prevent transfers
function transferFrom(...) public override {
  require(!isNonTransferable[tokenId], "Soulbound");
  super.transferFrom(from, to, tokenId);
}
```

### Unique Student IDs
```solidity
// Each student ID can only mint once
require(!studentIdExists[_studentId], "Already exists");
studentIdExists[_studentId] = true;
```

### Owner Verification
```solidity
function verifyOwnership(uint256 tokenId, address walletAddress)
    public view returns (bool)
{
    return tokenToWallet[tokenId] == walletAddress;
}
```

## Gas Costs (Estimated on Polygon Mumbai)

- Deploy Contract: ~2-3 MATIC
- Mint NFT: ~0.01-0.02 MATIC
- Verify Ownership: Free (view function)

## Next Steps

1. Deploy to Mumbai testnet
2. Test with frontend integration
3. Add error handling in frontend
4. Consider adding events listening
5. Plan for mainnet deployment

## Resources

- Remix IDE: https://remix.ethereum.org
- Polygon Faucet: https://faucet.polygon.technology/
- OpenZeppelin Docs: https://docs.openzeppelin.com/contracts/
- Hardhat Docs: https://hardhat.org/getting-started/
- PolygonScan Mumbai: https://mumbai.polygonscan.com/
