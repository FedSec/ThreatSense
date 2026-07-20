"""Send notifications via the Telegram Bot API."""

import logging
from typing import Optional
from urllib.parse import urlparse

import httpx

from app.models import DEFAULT_TELEGRAM_API_URL

logger = logging.getLogger(__name__)


def normalize_telegram_api_url(api_url: Optional[str]) -> str:
    """Return a usable Bot API base URL (scheme + host, no trailing slash)."""
    raw = (api_url or DEFAULT_TELEGRAM_API_URL).strip() or DEFAULT_TELEGRAM_API_URL
    if "://" not in raw:
        raw = f"https://{raw}"
    parsed = urlparse(raw)
    if not parsed.netloc:
        return DEFAULT_TELEGRAM_API_URL
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


def send_telegram_message(
    *,
    bot_token: Optional[str],
    chat_id: Optional[str],
    text: str,
    api_url: Optional[str] = None,
) -> bool:
    """POST sendMessage to Telegram (or a custom Bot API host)."""
    if not bot_token or not chat_id or not text:
        return False
    base = normalize_telegram_api_url(api_url)
    url = f"{base}/bot{bot_token}/sendMessage"
    try:
        r = httpx.post(
            url,
            json={"chat_id": chat_id, "text": text},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        if not data.get("ok", False):
            logger.warning("Telegram API error: %s", data)
            return False
        return True
    except Exception as e:
        logger.warning("Telegram notify failed: %s", e)
        return False


def send_scan_complete_telegram(
    *,
    bot_token: Optional[str],
    chat_id: Optional[str],
    api_url: Optional[str],
    scan_id: str,
    status: str,
    finding_count: int,
    high_or_critical: int = 0,
) -> bool:
    text = (
        f"ThreatSense scan {scan_id[:8]} → {status}\n"
        f"Findings: {finding_count} ({high_or_critical} high/critical)"
    )
    return send_telegram_message(
        bot_token=bot_token,
        chat_id=chat_id,
        text=text,
        api_url=api_url,
    )
