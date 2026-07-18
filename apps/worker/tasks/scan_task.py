import hashlib
import json
import logging
import os
import uuid
from datetime import datetime

from celery import shared_task
from sqlmodel import Session, create_engine, select

from models import Asset, Customer, Finding, Scan, ScanResult
from notify import notify_webhooks, send_email
from plugins.nmap_stub import NmapStub
from plugins.nuclei_scan import NucleiScan
from plugins.soc_rules import SocRules
from worker import celery_app

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://threatsense:threatsense_password@localhost:5432/threatsense",
)
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

PLUGINS = {
    "nmap_stub": NmapStub(),
    "nuclei_scan": NucleiScan(),
    "soc_rules": SocRules(),
}


def make_fingerprint(customer_id: str, title: str, affected_resource=None, cve_id=None) -> str:
    raw = "|".join(
        [
            customer_id or "",
            (title or "").strip().lower(),
            (affected_resource or "").strip().lower(),
            (cve_id or "").strip().upper(),
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _normalize_finding(raw: dict) -> dict:
    """Map plugin finding dicts into API Finding fields."""
    title = raw.get("title") or "Unnamed finding"
    severity = (raw.get("severity") or "info").lower()
    description = raw.get("description") or raw.get("evidence") or ""
    if not description and isinstance(raw.get("info"), dict):
        description = raw["info"].get("description") or ""

    cve_id = raw.get("cve") or raw.get("cve_id")
    classification = {}
    if isinstance(raw.get("info"), dict):
        classification = raw["info"].get("classification") or {}
        if not cve_id:
            cves = classification.get("cve-id") or classification.get("cve_id") or []
            if isinstance(cves, list) and cves:
                cve_id = cves[0]
            elif isinstance(cves, str):
                cve_id = cves

    cvss = raw.get("cvss") or raw.get("cvss_score")
    if cvss is None and classification:
        cvss = classification.get("cvss-score") or classification.get("cvss_score")

    affected = (
        raw.get("affected_resource")
        or raw.get("matched-at")
        or raw.get("host")
        or raw.get("url")
    )
    remediation = raw.get("remediation") or ""
    refs = raw.get("references") or raw.get("reference") or []
    if isinstance(refs, str):
        refs = [refs]
    tags = raw.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    finding_type = raw.get("finding_type") or raw.get("category") or "vulnerability"
    if finding_type in ("scanner_error", "general"):
        finding_type = "misconfiguration"

    return {
        "title": title,
        "description": description or title,
        "severity": severity if severity in {"critical", "high", "medium", "low", "info"} else "info",
        "finding_type": finding_type if finding_type in {
            "vulnerability", "misconfiguration", "weak_credential",
            "exposed_service", "cve", "compliance",
        } else "vulnerability",
        "cvss_score": float(cvss) if cvss is not None else None,
        "cve_id": cve_id,
        "cwe_id": raw.get("cwe_id") or raw.get("cwe"),
        "affected_resource": affected,
        "proof_of_concept": raw.get("proof_of_concept") or raw.get("evidence"),
        "remediation": remediation,
        "references": refs,
        "tags": tags,
    }


def _upsert_finding(session: Session, scan: Scan, asset: Asset, raw: dict) -> None:
    data = _normalize_finding(raw)
    fp = make_fingerprint(
        scan.customer_id, data["title"], data["affected_resource"], data["cve_id"]
    )
    existing = session.exec(
        select(Finding).where(
            Finding.customer_id == scan.customer_id,
            Finding.fingerprint == fp,
        )
    ).first()

    if existing:
        existing.scan_id = scan.id
        existing.description = data["description"]
        existing.severity = data["severity"]
        existing.cvss_score = data["cvss_score"] or existing.cvss_score
        existing.proof_of_concept = data["proof_of_concept"] or existing.proof_of_concept
        existing.remediation = data["remediation"] or existing.remediation
        existing.updated_at = datetime.utcnow()
        if existing.status == "resolved":
            existing.status = "open"
            existing.resolved_at = None
        session.add(existing)
        return

    finding = Finding(
        id=str(uuid.uuid4()),
        customer_id=scan.customer_id,
        asset_id=asset.id,
        scan_id=scan.id,
        fingerprint=fp,
        title=data["title"],
        description=data["description"],
        severity=data["severity"],
        finding_type=data["finding_type"],
        cvss_score=data["cvss_score"],
        cve_id=data["cve_id"],
        cwe_id=data["cwe_id"],
        affected_resource=data["affected_resource"],
        proof_of_concept=data["proof_of_concept"],
        remediation=data["remediation"],
        references=data["references"],
        tags=data["tags"],
        status="open",
    )
    session.add(finding)


def _notify(session: Session, scan: Scan, finding_count: int, high_crit: int) -> None:
    customer = session.get(Customer, scan.customer_id)
    if not customer:
        return
    to = customer.notify_email or customer.email
    send_email(
        to,
        f"ThreatSense scan {scan.status}: {scan.id[:8]}",
        f"Scan {scan.id} finished with status {scan.status}.\n"
        f"Findings: {finding_count} ({high_crit} high/critical).\n",
    )
    notify_webhooks(
        customer.slack_webhook_url,
        customer.discord_webhook_url,
        f"ThreatSense scan `{scan.id[:8]}` → *{scan.status}*\n"
        f"Findings: {finding_count} ({high_crit} high/critical)",
    )


@shared_task(name="scan.run")
def run_scan(scan_id: str):
    with Session(engine) as session:
        scan = session.get(Scan, scan_id)
        if not scan:
            logger.error("Scan not found: %s", scan_id)
            return

        if scan.status not in ("queued", "running"):
            return

        asset = session.get(Asset, scan.asset_id)
        if not asset:
            scan.status = "failed"
            scan.error_message = "Asset not found"
            scan.updated_at = datetime.utcnow()
            scan.completed_at = datetime.utcnow()
            session.add(scan)
            session.commit()
            return

        scan.status = "running"
        scan.started_at = datetime.utcnow()
        scan.updated_at = datetime.utcnow()
        session.add(scan)
        session.commit()

        try:
            params = scan.parameters or {}
            if isinstance(params, str):
                params = json.loads(params)
            params = dict(params)
            params["run_id"] = scan.id

            plugin = PLUGINS.get(scan.plugin)
            if not plugin:
                raise RuntimeError(f"Unknown plugin: {scan.plugin}")

            result = plugin.run(asset.kind, asset.value, params)

            session.add(
                ScanResult(
                    id=str(uuid.uuid4()),
                    scan_id=scan.id,
                    raw_output={
                        "artifact_path": result.artifact_path,
                        "finding_count": len(result.findings or []),
                    },
                )
            )

            for raw in result.findings or []:
                _upsert_finding(session, scan, asset, raw)

            scan.status = "completed"
            scan.completed_at = datetime.utcnow()
            scan.updated_at = datetime.utcnow()
            session.add(scan)
            session.commit()

            all_for_scan = session.exec(
                select(Finding).where(Finding.scan_id == scan.id)
            ).all()
            high_crit = sum(1 for f in all_for_scan if f.severity in ("high", "critical"))
            _notify(session, scan, len(all_for_scan), high_crit)

        except Exception as e:
            logger.exception("Scan failed: %s", scan_id)
            scan.status = "failed"
            scan.error_message = str(e)
            scan.completed_at = datetime.utcnow()
            scan.updated_at = datetime.utcnow()
            session.add(scan)
            session.commit()
            _notify(session, scan, 0, 0)


# Ensure celery discovers the task
celery_app.conf.imports = ("tasks.scan_task",)
