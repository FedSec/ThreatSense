import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# Load .env from repo root or apps/api
_ROOT = Path(__file__).resolve().parents[3]
_API_DIR = Path(__file__).resolve().parents[1]
load_dotenv(_ROOT / ".env")
load_dotenv(_API_DIR / ".env")


@lru_cache
def get_settings():
    return Settings()


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://threatsense:threatsense_password@localhost:5432/threatsense",
    )

    def __init__(self):
        # Prefer psycopg (v3) driver when URL omits a dialect driver
        if self.DATABASE_URL.startswith("postgresql://"):
            self.DATABASE_URL = self.DATABASE_URL.replace(
                "postgresql://", "postgresql+psycopg://", 1
            )
        elif self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = self.DATABASE_URL.replace(
                "postgres://", "postgresql+psycopg://", 1
            )
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "your-secret-key-change-this-in-production-use-openssl-rand-hex-32",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    ALLOWED_ORIGINS: list[str] = [
        o.strip()
        for o in os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000",
        ).split(",")
        if o.strip()
    ]
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # SMTP / Mailpit
    SMTP_HOST: str = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "1025"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM: str = os.getenv("SMTP_FROM", "noreply@threatsense.local")
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "false").lower() == "true"

    # Stripe
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_PRICE_STARTER: str = os.getenv("STRIPE_PRICE_STARTER", "")
    STRIPE_PRICE_PROFESSIONAL: str = os.getenv("STRIPE_PRICE_PROFESSIONAL", "")
    STRIPE_PRICE_ENTERPRISE: str = os.getenv("STRIPE_PRICE_ENTERPRISE", "")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Internal
    INTERNAL_API_SECRET: str = os.getenv("INTERNAL_API_SECRET", "threatsense-internal-dev-secret")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
