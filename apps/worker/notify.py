import logging
import os
import smtplib
from email.mime.text import MIMEText
from typing import Optional
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)

DEFAULT_TELEGRAM_API_URL = "https://api.telegram.org"


def send_email(to: str, subject: str, body: str) -> None:
    if not to:
        return
    host = os.getenv("SMTP_HOST", "localhost")
    port = int(os.getenv("SMTP_PORT", "1025"))
    from_addr = os.getenv("SMTP_FROM", "noreply@threatsense.local")
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = to
        with smtplib.SMTP(host, port, timeout=15) as server:
            server.sendmail(from_addr, [to], msg.as_string())
    except Exception as e:
        logger.warning("Worker email failed: %s", e)


def normalize_telegram_api_url(api_url: Optional[str]) -> str:
    raw = (api_url or DEFAULT_TELEGRAM_API_URL).strip() or DEFAULT_TELEGRAM_API_URL
    if "://" not in raw:
        raw = f"https://{raw}"
    parsed = urlparse(raw)
    if not parsed.netloc:
        return DEFAULT_TELEGRAM_API_URL
    return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")


def send_telegram(
    bot_token: Optional[str],
    chat_id: Optional[str],
    text: str,
    api_url: Optional[str] = None,
) -> None:
    if not bot_token or not chat_id or not text:
        return
    base = normalize_telegram_api_url(api_url)
    url = f"{base}/bot{bot_token}/sendMessage"
    try:
        r = httpx.post(url, json={"chat_id": chat_id, "text": text}, timeout=15)
        r.raise_for_status()
        data = r.json()
        if not data.get("ok", False):
            logger.warning("Telegram API error: %s", data)
    except Exception as e:
        logger.warning("Telegram notify failed: %s", e)


def notify_webhooks(
    slack_url: Optional[str],
    discord_url: Optional[str],
    text: str,
) -> None:
    if slack_url:
        try:
            httpx.post(slack_url, json={"text": text}, timeout=10)
        except Exception as e:
            logger.warning("Slack notify failed: %s", e)
    if discord_url:
        try:
            httpx.post(discord_url, json={"content": text}, timeout=10)
        except Exception as e:
            logger.warning("Discord notify failed: %s", e)
