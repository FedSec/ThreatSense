"""Notify customer after scan completion (email + webhooks)."""

from sqlmodel import Session, select, func

from app.models import Customer, Finding, Scan
from app.services.email import send_scan_complete_email
from app.services.webhooks import notify_scan_complete


def notify_after_scan(session: Session, scan_id: str) -> None:
    scan = session.get(Scan, scan_id)
    if not scan:
        return
    customer = session.get(Customer, scan.customer_id)
    if not customer:
        return

    finding_count = session.exec(
        select(func.count()).select_from(Finding).where(Finding.scan_id == scan_id)
    ).one()
    critical_count = session.exec(
        select(func.count())
        .select_from(Finding)
        .where(Finding.scan_id == scan_id, Finding.severity == "critical")
    ).one()
    high_or_critical = session.exec(
        select(func.count())
        .select_from(Finding)
        .where(
            Finding.scan_id == scan_id,
            Finding.severity.in_(("critical", "high")),
        )
    ).one()

    to = customer.notify_email or customer.email
    send_scan_complete_email(
        to,
        scan_id=scan.id,
        status=scan.status,
        finding_count=int(finding_count or 0),
        critical_count=int(critical_count or 0),
    )
    notify_scan_complete(
        slack_url=customer.slack_webhook_url,
        discord_url=customer.discord_webhook_url,
        scan_id=scan.id,
        status=scan.status,
        finding_count=int(finding_count or 0),
        high_or_critical=int(high_or_critical or 0),
    )
