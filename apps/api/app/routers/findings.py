from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/findings", tags=["findings"])


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    ACCEPTED_RISK = "accepted_risk"


class FindingType(str, Enum):
    VULNERABILITY = "vulnerability"
    MISCONFIGURATION = "misconfiguration"
    WEAK_CREDENTIAL = "weak_credential"
    EXPOSED_SERVICE = "exposed_service"
    CVE = "cve"
    COMPLIANCE = "compliance"


class FindingBase(BaseModel):
    title: str
    description: str
    severity: Severity
    finding_type: FindingType
    asset_id: str
    scan_id: str


class FindingCreate(FindingBase):
    cvss_score: Optional[float] = None
    cve_id: Optional[str] = None
    cwe_id: Optional[str] = None
    affected_resource: Optional[str] = None
    proof_of_concept: Optional[str] = None
    remediation: Optional[str] = None
    references: Optional[List[str]] = []
    tags: Optional[List[str]] = []


class Finding(FindingCreate):
    id: str
    status: FindingStatus
    created_at: str
    updated_at: str
    resolved_at: Optional[str] = None
    resolved_by: Optional[str] = None


class FindingUpdate(BaseModel):
    status: Optional[FindingStatus] = None


class FindingStats(BaseModel):
    total: int
    critical: int
    high: int
    medium: int
    low: int
    info: int
    open: int
    resolved: int
    in_progress: int


FINDINGS_DB: List[Finding] = []


@router.get("", response_model=List[Finding])
async def list_findings(
    severity: Optional[Severity] = None,
    status: Optional[FindingStatus] = None,
    asset_id: Optional[str] = None,
    scan_id: Optional[str] = None,
    finding_type: Optional[FindingType] = None,
    limit: int = Query(100, le=1000),
):
    results = FINDINGS_DB.copy()

    if severity:
        results = [f for f in results if f.severity == severity]
    if status:
        results = [f for f in results if f.status == status]
    if asset_id:
        results = [f for f in results if f.asset_id == asset_id]
    if scan_id:
        results = [f for f in results if f.scan_id == scan_id]
    if finding_type:
        results = [f for f in results if f.finding_type == finding_type]

    severity_order = {
        Severity.CRITICAL: 0,
        Severity.HIGH: 1,
        Severity.MEDIUM: 2,
        Severity.LOW: 3,
        Severity.INFO: 4,
    }
    results.sort(key=lambda x: (severity_order.get(x.severity, 99), x.created_at))

    return results[:limit]


@router.get("/stats", response_model=FindingStats)
async def get_finding_stats():
    return FindingStats(
        total=len(FINDINGS_DB),
        critical=sum(1 for f in FINDINGS_DB if f.severity == Severity.CRITICAL),
        high=sum(1 for f in FINDINGS_DB if f.severity == Severity.HIGH),
        medium=sum(1 for f in FINDINGS_DB if f.severity == Severity.MEDIUM),
        low=sum(1 for f in FINDINGS_DB if f.severity == Severity.LOW),
        info=sum(1 for f in FINDINGS_DB if f.severity == Severity.INFO),
        open=sum(1 for f in FINDINGS_DB if f.status == FindingStatus.OPEN),
        resolved=sum(1 for f in FINDINGS_DB if f.status == FindingStatus.RESOLVED),
        in_progress=sum(1 for f in FINDINGS_DB if f.status == FindingStatus.IN_PROGRESS),
    )


@router.post("", response_model=Finding)
async def create_finding(finding: FindingCreate):
    now = datetime.utcnow().isoformat()
    new_finding = Finding(
        id=str(uuid.uuid4()),
        **finding.dict(),
        status=FindingStatus.OPEN,
        created_at=now,
        updated_at=now,
    )
    FINDINGS_DB.append(new_finding)
    return new_finding


@router.get("/{finding_id}", response_model=Finding)
async def get_finding(finding_id: str):
    for f in FINDINGS_DB:
        if f.id == finding_id:
            return f
    raise HTTPException(status_code=404, detail="Finding not found")


@router.patch("/{finding_id}", response_model=Finding)
async def update_finding(finding_id: str, update: FindingUpdate):
    for f in FINDINGS_DB:
        if f.id == finding_id:
            if update.status:
                f.status = update.status
                if update.status == FindingStatus.RESOLVED:
                    f.resolved_at = datetime.utcnow().isoformat()
                    f.resolved_by = "current_user"
            f.updated_at = datetime.utcnow().isoformat()
            return f
    raise HTTPException(status_code=404, detail="Finding not found")


@router.delete("/{finding_id}")
async def mark_false_positive(finding_id: str):
    for f in FINDINGS_DB:
        if f.id == finding_id:
            f.status = FindingStatus.FALSE_POSITIVE
            f.updated_at = datetime.utcnow().isoformat()
            return {"message": "Finding marked as false positive"}
    raise HTTPException(status_code=404, detail="Finding not found")


@router.get("/export/json")
async def export_findings_json(
    severity: Optional[Severity] = None,
    status: Optional[FindingStatus] = None,
):
    findings = await list_findings(severity=severity, status=status)
    return {"findings": findings, "exported_at": datetime.utcnow().isoformat()}


@router.get("/export/csv")
async def export_findings_csv():
    import io
    import csv

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Title", "Severity", "Status", "Type", "CVSS Score",
        "CVE ID", "CWE ID", "Asset ID", "Scan ID", "Created", "Resolved",
    ])
    for f in FINDINGS_DB:
        writer.writerow([
            f.id, f.title, f.severity, f.status, f.finding_type,
            f.cvss_score or "N/A", f.cve_id or "N/A", f.cwe_id or "N/A",
            f.asset_id, f.scan_id, f.created_at, f.resolved_at or "N/A",
        ])
    return {"csv": output.getvalue(), "exported_at": datetime.utcnow().isoformat()}
