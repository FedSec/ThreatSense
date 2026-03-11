from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

router = APIRouter(prefix="/scans", tags=["scans"])

# Mock database for scans
MOCK_SCANS_DB = []

class ScanCreate(BaseModel):
    asset_id: str
    scan_type: str  # vuln_scan, soc, ptaas
    plugin: str
    requires_approval: bool = False
    parameters: Optional[Dict[str, Any]] = {}

class Scan(BaseModel):
    id: str
    asset_id: str
    scan_type: str
    plugin: str
    status: str  # queued, running, completed, failed, awaiting_approval
    parameters: Dict[str, Any] = {}
    created_at: str
    updated_at: str

@router.get("", response_model=List[Scan])
async def list_scans():
    """List all scans for the current customer"""
    # Sort by created_at descending (newest first)
    return sorted(MOCK_SCANS_DB, key=lambda x: x.created_at, reverse=True)

@router.post("", response_model=Scan)
async def create_scan(scan: ScanCreate):
    """Create a new scan"""
    now = datetime.utcnow().isoformat()

    new_scan = Scan(
        id=str(uuid.uuid4()),
        asset_id=scan.asset_id,
        scan_type=scan.scan_type,
        plugin=scan.plugin,
        status="awaiting_approval" if scan.requires_approval else "queued",
        parameters=scan.parameters or {},
        created_at=now,
        updated_at=now
    )
    MOCK_SCANS_DB.append(new_scan)

    # Auto-generate demo findings for new scans (for demo purposes)
    # In production, the worker would create findings based on actual scan results
    if not scan.requires_approval:
        try:
            from app.routers.findings import seed_demo_findings
            seed_demo_findings(scan.asset_id, new_scan.id)
        except Exception:
            pass  # Fail silently if findings module not available

    # In a real implementation, this would trigger the worker
    # For now, we'll just return the scan object
    return new_scan

@router.get("/{scan_id}", response_model=Scan)
async def get_scan(scan_id: str):
    """Get a specific scan by ID"""
    for scan in MOCK_SCANS_DB:
        if scan.id == scan_id:
            return scan
    raise HTTPException(status_code=404, detail="Scan not found")

@router.post("/{scan_id}/approve")
async def approve_scan(scan_id: str):
    """Approve a scan that requires approval"""
    for scan in MOCK_SCANS_DB:
        if scan.id == scan_id:
            if scan.status == "awaiting_approval":
                scan.status = "queued"
                scan.updated_at = datetime.utcnow().isoformat()
                return {"message": "Scan approved and queued"}
            else:
                raise HTTPException(status_code=400, detail="Scan is not awaiting approval")
    raise HTTPException(status_code=404, detail="Scan not found")
