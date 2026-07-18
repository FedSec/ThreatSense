import logging
import os
import smtplib
from email.mime.text import MIMEText
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


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
