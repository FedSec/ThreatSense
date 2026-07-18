"""In-process scan fallback when Celery/Redis is unavailable."""
import logging
import uuid
from datetime import datetime

from sqlmodel import Session, select

from app.database import engine
from app.models import Asset, Finding, FindingStatus, Scan, ScanResult, ScanStatus
from app.services.findings_util import make_fingerprint
from app.services.notifications import notify_after_scan

logger = logging.getLogger(__name__)


def run_scan_inprocess(scan_id: str) -> None:
    with Session(engine) as session:
        scan = session.get(Scan, scan_id)
        if not scan:
            return
        asset = session.get(Asset, scan.asset_id)
        if not asset:
            scan.status = ScanStatus.FAILED.value
            scan.error_message = "Asset not found"
            scan.completed_at = datetime.utcnow()
            session.add(scan)
            session.commit()
            return

        scan.status = ScanStatus.RUNNING.value
        scan.started_at = datetime.utcnow()
        scan.updated_at = datetime.utcnow()
        session.add(scan)
        session.commit()

        try:
            from app.scanner import get_scanner

            scanner = get_scanner()
            params = scan.parameters or {}
            result = scanner.scan(
                target=asset.value,
                severities=params.get("severities"),
                tags=params.get("tags", "").split(",") if params.get("tags") else None,
                exclude_tags=(
                    params.get("exclude_tags", "").split(",")
                    if params.get("exclude_tags")
                    else None
                ),
                rate_limit=params.get("rate_limit", 50),
                timeout=params.get("timeout", 10),
                retries=params.get("retries", 2),
            )

            session.add(
                ScanResult(
                    id=str(uuid.uuid4()),
                    scan_id=scan.id,
                    raw_output={"success": result.get("success"), "count": len(result.get("results", []))},
                )
            )

            if not result.get("success"):
                scan.status = ScanStatus.FAILED.value
                scan.error_message = result.get("error") or "Scan failed"
            else:
                for raw in result.get("results", []):
                    parsed = scanner.parse_finding(raw)
                    _upsert(session, scan, asset, parsed)
                scan.status = ScanStatus.COMPLETED.value

            scan.completed_at = datetime.utcnow()
            scan.updated_at = datetime.utcnow()
            session.add(scan)
            session.commit()
            notify_after_scan(session, scan.id)
        except Exception as e:
            logger.exception("In-process scan failed")
            scan.status = ScanStatus.FAILED.value
            scan.error_message = str(e)
            scan.completed_at = datetime.utcnow()
            scan.updated_at = datetime.utcnow()
            session.add(scan)
            session.commit()
            notify_after_scan(session, scan.id)


def _upsert(session: Session, scan: Scan, asset: Asset, parsed: dict) -> None:
    title = parsed.get("title") or "Unnamed finding"
    affected = parsed.get("affected_resource")
    cve_id = parsed.get("cve_id")
    fp = make_fingerprint(scan.customer_id, title, affected, cve_id)
    existing = session.exec(
        select(Finding).where(
            Finding.customer_id == scan.customer_id,
            Finding.fingerprint == fp,
        )
    ).first()
    if existing:
        existing.scan_id = scan.id
        existing.description = parsed.get("description") or existing.description
        existing.severity = parsed.get("severity") or existing.severity
        existing.updated_at = datetime.utcnow()
        session.add(existing)
        return

    session.add(
        Finding(
            id=str(uuid.uuid4()),
            customer_id=scan.customer_id,
            asset_id=asset.id,
            scan_id=scan.id,
            fingerprint=fp,
            title=title,
            description=parsed.get("description") or title,
            severity=parsed.get("severity") or "info",
            finding_type="vulnerability",
            cvss_score=parsed.get("cvss_score"),
            cve_id=cve_id,
            cwe_id=parsed.get("cwe_id"),
            affected_resource=affected,
            proof_of_concept=parsed.get("proof_of_concept"),
            remediation=parsed.get("remediation"),
            references=parsed.get("references") or [],
            tags=parsed.get("tags") or [],
            status=FindingStatus.OPEN.value,
        )
    )
