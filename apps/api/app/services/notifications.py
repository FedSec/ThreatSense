"""Notify customer after scan completion (email or Telegram + webhooks)."""

from sqlmodel import Session, select, func

from app.models import Customer, Finding, NotifyChannel, Scan
from app.services.email import send_scan_complete_email
from app.services.telegram import send_scan_complete_telegram
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

    channel = (customer.notify_channel or NotifyChannel.EMAIL.value).lower()
    if channel == NotifyChannel.TELEGRAM.value:
        send_scan_complete_telegram(
            bot_token=customer.telegram_bot_token,
            chat_id=customer.telegram_chat_id,
            api_url=customer.telegram_api_url,
            scan_id=scan.id,
            status=scan.status,
            finding_count=int(finding_count or 0),
            high_or_critical=int(high_or_critical or 0),
        )
    else:
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
