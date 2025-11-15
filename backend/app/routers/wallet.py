"""
Apple Wallet integration endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.auth import get_current_user
from app.models import User
import os
import json

router = APIRouter(prefix="/api/wallet", tags=["wallet"])


class AppleWalletPassData(BaseModel):
    """Model for Apple Wallet pass data."""
    nft_token_id: str = None


@router.post("/generate-pkpass-data")
async def generate_apple_wallet_pass_data(
    data: AppleWalletPassData,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate Apple Wallet pass.json data structure.
    This returns the JSON data needed to create a .pkpass file.
    """
    try:
        # Convert student ID to binary for PDF417 barcode
        student_id = current_user.student_id
        binary = bin(int(student_id))[2:]

        # Generate pass.json structure
        pass_data = {
            "formatVersion": 1,
            "passTypeIdentifier": os.getenv("APPLE_PASS_TYPE_ID", "pass.edu.wisc.wiscard"),
            "serialNumber": student_id,
            "teamIdentifier": os.getenv("APPLE_TEAM_ID", "YOUR_TEAM_ID"),
            "organizationName": "University of Wisconsin-Madison",
            "description": "UW-Madison Virtual WisCard",
            "logoText": "WisCard",
            "backgroundColor": "rgb(197, 5, 12)",  # UW Red
            "foregroundColor": "rgb(255, 255, 255)",  # White
            "labelColor": "rgb(255, 255, 255)",
            "barcode": {
                "message": binary,
                "format": "PKBarcodeFormatPDF417",
                "messageEncoding": "iso-8859-1",
                "altText": f"Student ID: {student_id}"
            },
            "barcodes": [
                {
                    "message": binary,
                    "format": "PKBarcodeFormatPDF417",
                    "messageEncoding": "iso-8859-1",
                    "altText": f"Student ID: {student_id}"
                }
            ],
            "generic": {
                "primaryFields": [
                    {
                        "key": "name",
                        "label": "Name",
                        "value": current_user.full_name
                    }
                ],
                "secondaryFields": [
                    {
                        "key": "studentid",
                        "label": "Student ID",
                        "value": student_id
                    },
                    {
                        "key": "netid",
                        "label": "NetID",
                        "value": current_user.netid
                    }
                ],
                "auxiliaryFields": [
                    {
                        "key": "expires",
                        "label": "Expires",
                        "value": current_user.expiration_date.strftime("%m/%d/%Y"),
                        "dateStyle": "PKDateStyleShort"
                    }
                ],
                "backFields": [
                    {
                        "key": "binary",
                        "label": "Binary Code",
                        "value": binary
                    },
                    {
                        "key": "email",
                        "label": "Email",
                        "value": current_user.email
                    }
                ]
            }
        }

        # Add NFT info if provided
        if data.nft_token_id:
            pass_data["generic"]["backFields"].extend([
                {
                    "key": "nft",
                    "label": "NFT Token ID",
                    "value": data.nft_token_id
                },
                {
                    "key": "blockchain",
                    "label": "Blockchain",
                    "value": "Polygon (Soulbound)"
                }
            ])

        return {
            "success": True,
            "pass_data": pass_data,
            "binary_code": binary,
            "student_id": student_id,
            "instructions": [
                "Save pass.json to a directory",
                "Add icon.png and icon@2x.png images",
                "Create manifest.json with SHA1 hashes",
                "Sign with Apple certificate",
                "Zip as .pkpass file"
            ],
            "note": "Full .pkpass generation requires Apple Developer certificate"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate pass data: {str(e)}"
        )


@router.get("/barcode-data")
async def get_barcode_data(
    current_user: User = Depends(get_current_user)
):
    """Get barcode data for wallet pass."""
    try:
        student_id = current_user.student_id
        binary = bin(int(student_id))[2:]

        return {
            "student_id": student_id,
            "binary": binary,
            "format": "PDF417",
            "encoding": "iso-8859-1",
            "message": binary,
            "alt_text": f"Student ID: {student_id}"
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to generate barcode data: {str(e)}"
        )
