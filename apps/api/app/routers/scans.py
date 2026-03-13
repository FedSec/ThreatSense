from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

router = APIRouter(prefix="/scans", tags=["scans"])

SCANS_DB: List[dict] = []


class ScanCreate(BaseModel):
    asset_id: str
    scan_type: str
    plugin: str
    requires_approval: bool = False
    parameters: Optional[Dict[str, Any]] = {}


class Scan(BaseModel):
    id: str
    asset_id: str
    scan_type: str
    plugin: str
    status: str
    parameters: Dict[str, Any] = {}
    created_at: str
    updated_at: str


def _find_scan(scan_id: str) -> Optional[dict]:
    return next((s for s in SCANS_DB if s["id"] == scan_id), None)


def _set_status(scan_id: str, status: str):
    s = _find_scan(scan_id)
    if s:
        s["status"] = status
        s["updated_at"] = datetime.utcnow().isoformat()


def _run_nuclei(scan_id: str, asset_id: str, target: str, parameters: dict):
    """Run Nuclei and store real findings. Executed in a background thread."""
    from app.scanner import get_scanner
    from app.routers.findings import FINDINGS_DB, Finding, FindingStatus, FindingType, Severity

    _set_status(scan_id, "running")

    scanner = get_scanner()
    result = scanner.scan(
        target=target,
        severities=parameters.get("severities"),
        tags=parameters.get("tags", "").split(",") if parameters.get("tags") else None,
        exclude_tags=parameters.get("exclude_tags", "").split(",") if parameters.get("exclude_tags") else None,
        rate_limit=parameters.get("rate_limit", 50),
        timeout=parameters.get("timeout", 10),
        retries=parameters.get("retries", 2),
    )

    if not result.get("success"):
        _set_status(scan_id, "failed")
        return

    severity_map = {
        "critical": Severity.CRITICAL,
        "high": Severity.HIGH,
        "medium": Severity.MEDIUM,
        "low": Severity.LOW,
        "info": Severity.INFO,
    }

    now = datetime.utcnow().isoformat()
    for raw in result.get("results", []):
        parsed = scanner.parse_finding(raw)
        sev = severity_map.get(parsed.get("severity", "info"), Severity.INFO)
        finding = Finding(
            id=str(uuid.uuid4()),
            asset_id=asset_id,
            scan_id=scan_id,
            title=parsed.get("title", "Unnamed finding"),
            description=parsed.get("description", ""),
            severity=sev,
            finding_type=FindingType.VULNERABILITY,
            cvss_score=parsed.get("cvss_score"),
            cve_id=parsed.get("cve_id"),
            cwe_id=parsed.get("cwe_id"),
            affected_resource=parsed.get("affected_resource"),
            proof_of_concept=parsed.get("proof_of_concept"),
            remediation=parsed.get("remediation"),
            references=parsed.get("references", []),
            tags=parsed.get("tags", []),
            status=FindingStatus.OPEN,
            created_at=now,
            updated_at=now,
        )
        FINDINGS_DB.append(finding)

    _set_status(scan_id, "completed")


@router.get("", response_model=List[Scan])
async def list_scans():
    return sorted([Scan(**s) for s in SCANS_DB], key=lambda x: x.created_at, reverse=True)


@router.post("", response_model=Scan)
async def create_scan(scan: ScanCreate, background_tasks: BackgroundTasks):
    from app.routers.assets import MOCK_ASSETS_DB

    now = datetime.utcnow().isoformat()
    scan_id = str(uuid.uuid4())
    status = "awaiting_approval" if scan.requires_approval else "queued"

    record = {
        "id": scan_id,
        "asset_id": scan.asset_id,
        "scan_type": scan.scan_type,
        "plugin": scan.plugin,
        "status": status,
        "parameters": scan.parameters or {},
        "created_at": now,
        "updated_at": now,
    }
    SCANS_DB.append(record)

    if not scan.requires_approval:
        asset = next((a for a in MOCK_ASSETS_DB if a.id == scan.asset_id), None)
        if asset:
            background_tasks.add_task(
                _run_nuclei, scan_id, asset.id, asset.value, scan.parameters or {}
            )

    return Scan(**record)


@router.get("/{scan_id}", response_model=Scan)
async def get_scan(scan_id: str):
    s = _find_scan(scan_id)
    if not s:
        raise HTTPException(status_code=404, detail="Scan not found")
    return Scan(**s)


@router.post("/{scan_id}/approve")
async def approve_scan(scan_id: str, background_tasks: BackgroundTasks):
    from app.routers.assets import MOCK_ASSETS_DB

    s = _find_scan(scan_id)
    if not s:
        raise HTTPException(status_code=404, detail="Scan not found")
    if s["status"] != "awaiting_approval":
        raise HTTPException(status_code=400, detail="Scan is not awaiting approval")

    _set_status(scan_id, "queued")

    asset = next((a for a in MOCK_ASSETS_DB if a.id == s["asset_id"]), None)
    if asset:
        background_tasks.add_task(
            _run_nuclei, scan_id, asset.id, asset.value, s["parameters"]
        )

    return {"message": "Scan approved and queued"}
