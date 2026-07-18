import csv
import io
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select, func

from app.database import get_session
from app.deps import get_current_customer, get_current_user
from app.models import Customer, Finding, FindingStatus, User
from app.schemas import (
    FindingAggregate,
    FindingCreate,
    FindingOut,
    FindingStats,
    FindingUpdate,
)
from app.services.findings_util import make_fingerprint

router = APIRouter(prefix="/findings", tags=["findings"])


def _to_out(f: Finding) -> FindingOut:
    return FindingOut(
        id=f.id,
        customer_id=f.customer_id,
        asset_id=f.asset_id,
        scan_id=f.scan_id,
        fingerprint=f.fingerprint,
        title=f.title,
        description=f.description,
        severity=f.severity,
        status=f.status,
        finding_type=f.finding_type,
        cvss_score=f.cvss_score,
        cve_id=f.cve_id,
        cwe_id=f.cwe_id,
        affected_resource=f.affected_resource,
        proof_of_concept=f.proof_of_concept,
        remediation=f.remediation,
        references=f.references or [],
        tags=f.tags or [],
        created_at=f.created_at,
        updated_at=f.updated_at,
        resolved_at=f.resolved_at,
        resolved_by=f.resolved_by,
    )


def _base_query(customer_id: str):
    return select(Finding).where(Finding.customer_id == customer_id)


@router.get("", response_model=list[FindingOut])
async def list_findings(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    asset_id: Optional[str] = None,
    scan_id: Optional[str] = None,
    finding_type: Optional[str] = None,
    limit: int = Query(100, le=1000),
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    q = _base_query(customer.id)
    if severity:
        q = q.where(Finding.severity == severity)
    if status:
        q = q.where(Finding.status == status)
    if asset_id:
        q = q.where(Finding.asset_id == asset_id)
    if scan_id:
        q = q.where(Finding.scan_id == scan_id)
    if finding_type:
        q = q.where(Finding.finding_type == finding_type)

    findings = session.exec(q.order_by(Finding.created_at.desc()).limit(limit)).all()

    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    findings = sorted(
        findings,
        key=lambda x: (severity_order.get(x.severity, 99), x.created_at),
    )
    return [_to_out(f) for f in findings]


@router.get("/stats", response_model=FindingStats)
async def get_finding_stats(
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    cid = customer.id

    def count_where(**kwargs):
        q = select(func.count()).select_from(Finding).where(Finding.customer_id == cid)
        for k, v in kwargs.items():
            q = q.where(getattr(Finding, k) == v)
        return int(session.exec(q).one() or 0)

    return FindingStats(
        total=count_where(),
        critical=count_where(severity="critical"),
        high=count_where(severity="high"),
        medium=count_where(severity="medium"),
        low=count_where(severity="low"),
        info=count_where(severity="info"),
        open=count_where(status=FindingStatus.OPEN.value),
        resolved=count_where(status=FindingStatus.RESOLVED.value),
        in_progress=count_where(status=FindingStatus.IN_PROGRESS.value),
    )


@router.get("/aggregate", response_model=FindingAggregate)
async def aggregate_findings(
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    cid = customer.id
    findings = session.exec(select(Finding).where(Finding.customer_id == cid)).all()

    by_severity: dict[str, int] = {}
    by_status: dict[str, int] = {}
    by_type: dict[str, int] = {}
    by_asset: dict[str, int] = {}
    for f in findings:
        by_severity[f.severity] = by_severity.get(f.severity, 0) + 1
        by_status[f.status] = by_status.get(f.status, 0) + 1
        by_type[f.finding_type] = by_type.get(f.finding_type, 0) + 1
        by_asset[f.asset_id] = by_asset.get(f.asset_id, 0) + 1

    return FindingAggregate(
        by_severity=by_severity,
        by_status=by_status,
        by_type=by_type,
        by_asset=by_asset,
    )


@router.post("", response_model=FindingOut)
async def create_finding(
    body: FindingCreate,
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    fp = make_fingerprint(
        customer.id, body.title, body.affected_resource, body.cve_id
    )
    existing = session.exec(
        select(Finding).where(
            Finding.customer_id == customer.id,
            Finding.fingerprint == fp,
        )
    ).first()
    if existing:
        existing.scan_id = body.scan_id
        existing.updated_at = datetime.utcnow()
        existing.description = body.description
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return _to_out(existing)

    finding = Finding(
        customer_id=customer.id,
        asset_id=body.asset_id,
        scan_id=body.scan_id,
        fingerprint=fp,
        title=body.title,
        description=body.description,
        severity=body.severity,
        finding_type=body.finding_type,
        cvss_score=body.cvss_score,
        cve_id=body.cve_id,
        cwe_id=body.cwe_id,
        affected_resource=body.affected_resource,
        proof_of_concept=body.proof_of_concept,
        remediation=body.remediation,
        references=body.references or [],
        tags=body.tags or [],
        status=FindingStatus.OPEN.value,
    )
    session.add(finding)
    session.commit()
    session.refresh(finding)
    return _to_out(finding)


@router.get("/export/json")
async def export_findings_json(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    findings = await list_findings(
        severity=severity,
        status=status,
        customer=customer,
        session=session,
    )
    return {"findings": findings, "exported_at": datetime.utcnow().isoformat()}


@router.get("/export/csv")
async def export_findings_csv(
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    findings = session.exec(
        select(Finding).where(Finding.customer_id == customer.id)
    ).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Title", "Severity", "Status", "Type", "CVSS Score",
        "CVE ID", "CWE ID", "Asset ID", "Scan ID", "Created", "Resolved",
    ])
    for f in findings:
        writer.writerow([
            f.id, f.title, f.severity, f.status, f.finding_type,
            f.cvss_score or "N/A", f.cve_id or "N/A", f.cwe_id or "N/A",
            f.asset_id, f.scan_id,
            f.created_at.isoformat() if f.created_at else "",
            f.resolved_at.isoformat() if f.resolved_at else "N/A",
        ])

    data = output.getvalue()
    return StreamingResponse(
        iter([data]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=threatsense-findings.csv"},
    )


@router.get("/export/pdf")
async def export_findings_pdf(
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    findings = session.exec(
        select(Finding)
        .where(Finding.customer_id == customer.id)
        .order_by(Finding.severity)
        .limit(100)
    ).all()
    stats = await get_finding_stats(customer=customer, session=session)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "ThreatSense Findings Report")
    y -= 24
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Company: {customer.company_name}")
    y -= 14
    c.drawString(50, y, f"Generated: {datetime.utcnow().isoformat()}Z")
    y -= 20
    c.drawString(
        50,
        y,
        f"Total: {stats.total} | Critical: {stats.critical} | High: {stats.high} | "
        f"Medium: {stats.medium} | Open: {stats.open}",
    )
    y -= 30

    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "Top findings")
    y -= 18
    c.setFont("Helvetica", 9)

    for f in findings[:40]:
        if y < 60:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 9)
        line = f"[{f.severity.upper()}] {f.title[:80]}"
        c.drawString(50, y, line)
        y -= 12
        if f.cve_id:
            c.drawString(60, y, f"CVE: {f.cve_id}")
            y -= 12

    c.save()
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=threatsense-findings.pdf"},
    )


@router.get("/{finding_id}", response_model=FindingOut)
async def get_finding(
    finding_id: str,
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    f = session.get(Finding, finding_id)
    if not f or f.customer_id != customer.id:
        raise HTTPException(status_code=404, detail="Finding not found")
    return _to_out(f)


@router.patch("/{finding_id}", response_model=FindingOut)
async def update_finding(
    finding_id: str,
    update: FindingUpdate,
    customer: Customer = Depends(get_current_customer),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    f = session.get(Finding, finding_id)
    if not f or f.customer_id != customer.id:
        raise HTTPException(status_code=404, detail="Finding not found")
    if update.status:
        f.status = update.status
        if update.status == FindingStatus.RESOLVED.value:
            f.resolved_at = datetime.utcnow()
            f.resolved_by = user.email
    f.updated_at = datetime.utcnow()
    session.add(f)
    session.commit()
    session.refresh(f)
    return _to_out(f)


@router.delete("/{finding_id}")
async def mark_false_positive(
    finding_id: str,
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    f = session.get(Finding, finding_id)
    if not f or f.customer_id != customer.id:
        raise HTTPException(status_code=404, detail="Finding not found")
    f.status = FindingStatus.FALSE_POSITIVE.value
    f.updated_at = datetime.utcnow()
    session.add(f)
    session.commit()
    return {"message": "Finding marked as false positive"}
