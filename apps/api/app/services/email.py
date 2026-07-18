import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import get_settings

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body_text: str, body_html: str | None = None) -> bool:
    """Send email via SMTP. Returns True on success."""
    if not to:
        return False
    settings = get_settings()
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to
    msg.attach(MIMEText(body_text, "plain"))
    if body_html:
        msg.attach(MIMEText(body_html, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            if settings.SMTP_TLS:
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, [to], msg.as_string())
        logger.info("Email sent to %s: %s", to, subject)
        return True
    except Exception as e:
        logger.warning("Failed to send email to %s: %s", to, e)
        return False


def send_welcome_email(to: str, full_name: str, company_name: str) -> bool:
    subject = "Welcome to ThreatSense"
    text = (
        f"Hi {full_name},\n\n"
        f"Welcome to ThreatSense! Your company account for {company_name} is ready.\n"
        f"Log in to start adding assets and running vulnerability scans.\n\n"
        f"— The ThreatSense Team"
    )
    html = f"<p>Hi {full_name},</p><p>Welcome to ThreatSense! Your company account for <b>{company_name}</b> is ready.</p>"
    return send_email(to, subject, text, html)


def send_scan_complete_email(
    to: str,
    scan_id: str,
    status: str,
    finding_count: int,
    critical_count: int = 0,
) -> bool:
    subject = f"ThreatSense scan {status}: {scan_id[:8]}"
    text = (
        f"Your scan ({scan_id}) finished with status: {status}.\n"
        f"Findings: {finding_count} total, {critical_count} critical.\n"
        f"Review them in the ThreatSense dashboard.\n"
    )
    return send_email(to, subject, text)
