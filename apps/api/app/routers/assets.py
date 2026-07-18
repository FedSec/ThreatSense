from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.deps import get_current_customer
from app.models import Asset, Customer
from app.schemas import AssetCreate, AssetOut

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("", response_model=list[AssetOut])
async def list_assets(
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    assets = session.exec(
        select(Asset).where(Asset.customer_id == customer.id)
    ).all()
    return assets


@router.post("", response_model=AssetOut)
async def create_asset(
    body: AssetCreate,
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    asset = Asset(
        customer_id=customer.id,
        kind=body.kind,
        value=body.value,
        verified=False,
    )
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return asset


@router.get("/{asset_id}", response_model=AssetOut)
async def get_asset(
    asset_id: str,
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    asset = session.get(Asset, asset_id)
    if not asset or asset.customer_id != customer.id:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.delete("/{asset_id}")
async def delete_asset(
    asset_id: str,
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    asset = session.get(Asset, asset_id)
    if not asset or asset.customer_id != customer.id:
        raise HTTPException(status_code=404, detail="Asset not found")
    session.delete(asset)
    session.commit()
    return {"message": "Asset deleted"}
