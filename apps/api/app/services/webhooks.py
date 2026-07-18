import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


def notify_slack(webhook_url: Optional[str], text: str) -> bool:
    if not webhook_url:
        return False
    try:
        r = httpx.post(webhook_url, json={"text": text}, timeout=10)
        r.raise_for_status()
        return True
    except Exception as e:
        logger.warning("Slack webhook failed: %s", e)
        return False


def notify_discord(webhook_url: Optional[str], content: str) -> bool:
    if not webhook_url:
        return False
    try:
        r = httpx.post(webhook_url, json={"content": content}, timeout=10)
        r.raise_for_status()
        return True
    except Exception as e:
        logger.warning("Discord webhook failed: %s", e)
        return False


def notify_scan_complete(
    *,
    slack_url: Optional[str],
    discord_url: Optional[str],
    scan_id: str,
    status: str,
    finding_count: int,
    high_or_critical: int,
) -> None:
    msg = (
        f"ThreatSense scan `{scan_id[:8]}` → *{status}*\n"
        f"Findings: {finding_count} ({high_or_critical} high/critical)"
    )
    notify_slack(slack_url, msg)
    notify_discord(discord_url, msg)
