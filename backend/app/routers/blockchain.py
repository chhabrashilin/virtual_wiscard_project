"""
Blockchain and NFT integration endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.auth import get_current_user
from app.models import User
import os

router = APIRouter(prefix="/api/blockchain", tags=["blockchain"])


class MintNFTRequest(BaseModel):
    """Request model for minting NFT."""
    wallet_address: str


class BinaryConversionResponse(BaseModel):
    """Response model for binary conversion."""
    student_id: str
    binary: str
    barcode_type: str


@router.post("/student-id-to-binary")
def convert_student_id_to_binary(
    current_user: User = Depends(get_current_user)
):
    """Convert student ID to binary representation for PDF417 barcode."""
    try:
        student_id = current_user.student_id
        # Convert student ID to binary (remove '0b' prefix)
        binary = bin(int(student_id))[2:]

        return {
            "student_id": student_id,
            "binary": binary,
            "binary_length": len(binary),
            "barcode_type": "PDF417",
            "description": "Binary representation for secure QR/barcode encoding"
        }
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid student ID format. Must be numeric."
        )


@router.post("/mint-nft")
async def mint_wiscard_nft(
    request: MintNFTRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Prepare data for minting WisCard NFT on blockchain.
    Returns all necessary data to mint a soulbound (non-transferable) NFT.
    """
    try:
        student_id = current_user.student_id
        binary = bin(int(student_id))[2:]

        # Prepare NFT metadata
        nft_metadata = {
            "wallet_address": request.wallet_address,
            "student_name": current_user.full_name,
            "student_id": student_id,
            "binary_representation": binary,
            "issue_date": current_user.created_at.isoformat(),
            "expiry_date": current_user.expiration_date.isoformat(),
            "email": current_user.email,
            "netid": current_user.netid,
            "contract_address": os.getenv("CONTRACT_ADDRESS", ""),
            "chain_id": int(os.getenv("CHAIN_ID", "80001")),
            "network": "Polygon Mumbai Testnet",
            "token_type": "Soulbound (Non-Transferable)"
        }

        return {
            "success": True,
            "message": "NFT metadata prepared for minting",
            "metadata": nft_metadata,
            "next_steps": [
                "Connect MetaMask wallet",
                "Call smart contract mintWisCard() function",
                "Sign transaction to mint NFT",
                "NFT will be bound to your wallet address"
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to prepare NFT data: {str(e)}"
        )


@router.get("/verify-nft/{wallet_address}")
async def verify_nft_ownership(
    wallet_address: str,
    current_user: User = Depends(get_current_user)
):
    """
    Verify NFT ownership for a wallet address.
    In production, this would query the smart contract on-chain.
    """
    # This is a placeholder - in production, use web3.py to query the smart contract
    return {
        "wallet_address": wallet_address,
        "student_id": current_user.student_id,
        "has_nft": True,  # Placeholder
        "is_soulbound": True,
        "verification_status": "pending_blockchain_integration",
        "message": "Connect smart contract for on-chain verification"
    }
