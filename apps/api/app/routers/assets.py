from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import uuid

router = APIRouter(prefix="/assets", tags=["assets"])

# Mock database for assets
MOCK_ASSETS_DB = []

class AssetCreate(BaseModel):
    kind: str
    value: str

class Asset(BaseModel):
    id: str
    kind: str
    value: str
    verified: bool = False

@router.get("", response_model=List[Asset])
async def list_assets():
    """List all assets for the current customer"""
    return MOCK_ASSETS_DB

@router.post("", response_model=Asset)
async def create_asset(asset: AssetCreate):
    """Create a new asset"""
    new_asset = Asset(
        id=str(uuid.uuid4()),
        kind=asset.kind,
        value=asset.value,
        verified=False
    )
    MOCK_ASSETS_DB.append(new_asset)
    return new_asset

@router.get("/{asset_id}", response_model=Asset)
async def get_asset(asset_id: str):
    """Get a specific asset by ID"""
    for asset in MOCK_ASSETS_DB:
        if asset.id == asset_id:
            return asset
    raise HTTPException(status_code=404, detail="Asset not found")
