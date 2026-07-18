import hashlib
from typing import Optional


def make_fingerprint(
    customer_id: str,
    title: str,
    affected_resource: Optional[str] = None,
    cve_id: Optional[str] = None,
) -> str:
    raw = "|".join(
        [
            customer_id or "",
            (title or "").strip().lower(),
            (affected_resource or "").strip().lower(),
            (cve_id or "").strip().upper(),
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
