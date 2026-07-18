from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.deps import get_current_customer
from app.models import Asset, Customer, Scan, ScanStatus
from app.schemas import ScanCreate, ScanOut
from app.services.billing import assert_plugin_allowed
from app.services.celery_client import enqueue_scan
from app.services.scan_runner import run_scan_inprocess

router = APIRouter(prefix="/scans", tags=["scans"])


def _queue_or_fallback(scan_id: str, background_tasks: BackgroundTasks) -> None:
    if not enqueue_scan(scan_id):
        background_tasks.add_task(run_scan_inprocess, scan_id)


def _to_out(scan: Scan) -> ScanOut:
    return ScanOut(
        id=scan.id,
        asset_id=scan.asset_id,
        scan_type=scan.scan_type,
        plugin=scan.plugin,
        status=scan.status,
        parameters=scan.parameters or {},
        created_at=scan.created_at,
        updated_at=scan.updated_at,
        started_at=scan.started_at,
        completed_at=scan.completed_at,
        error_message=scan.error_message,
    )


@router.get("", response_model=list[ScanOut])
async def list_scans(
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    scans = session.exec(
        select(Scan)
        .where(Scan.customer_id == customer.id)
        .order_by(Scan.created_at.desc())
    ).all()
    return [_to_out(s) for s in scans]


@router.post("", response_model=ScanOut)
async def create_scan(
    body: ScanCreate,
    background_tasks: BackgroundTasks,
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    asset = session.get(Asset, body.asset_id)
    if not asset or asset.customer_id != customer.id:
        raise HTTPException(status_code=404, detail="Asset not found")

    assert_plugin_allowed(customer.plan, body.plugin)

    status = (
        ScanStatus.AWAITING_APPROVAL.value
        if body.requires_approval
        else ScanStatus.QUEUED.value
    )
    scan = Scan(
        customer_id=customer.id,
        asset_id=body.asset_id,
        scan_type=body.scan_type,
        plugin=body.plugin,
        status=status,
        parameters=body.parameters or {},
        requires_approval=body.requires_approval,
    )
    session.add(scan)
    session.commit()
    session.refresh(scan)

    if not body.requires_approval:
        _queue_or_fallback(scan.id, background_tasks)

    return _to_out(scan)


@router.get("/{scan_id}", response_model=ScanOut)
async def get_scan(
    scan_id: str,
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    scan = session.get(Scan, scan_id)
    if not scan or scan.customer_id != customer.id:
        raise HTTPException(status_code=404, detail="Scan not found")
    return _to_out(scan)


@router.post("/{scan_id}/approve", response_model=ScanOut)
async def approve_scan(
    scan_id: str,
    background_tasks: BackgroundTasks,
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    scan = session.get(Scan, scan_id)
    if not scan or scan.customer_id != customer.id:
        raise HTTPException(status_code=404, detail="Scan not found")
    if scan.status != ScanStatus.AWAITING_APPROVAL.value:
        raise HTTPException(status_code=400, detail="Scan is not awaiting approval")

    scan.status = ScanStatus.QUEUED.value
    scan.updated_at = datetime.utcnow()
    session.add(scan)
    session.commit()
    session.refresh(scan)

    _queue_or_fallback(scan.id, background_tasks)

    return _to_out(scan)
