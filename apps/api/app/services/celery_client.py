import logging

from celery import Celery

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

celery_client = Celery(
    "threatsense_api",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.REDIS_URL,
)


def enqueue_scan(scan_id: str) -> bool:
    """Enqueue scan.run on the worker. Returns False if broker unavailable."""
    try:
        celery_client.send_task("scan.run", args=[scan_id])
        return True
    except Exception as e:
        logger.error("Failed to enqueue scan %s: %s", scan_id, e)
        return False
