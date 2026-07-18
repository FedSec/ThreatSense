"""SQLModel tables aligned with apps/api/app/models.py."""
from datetime import datetime
from typing import List, Optional
import uuid

from sqlalchemy import Column, JSON, UniqueConstraint
from sqlmodel import Field, SQLModel


class Customer(SQLModel, table=True):
    __tablename__ = "customers"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    company_name: str
    email: str = Field(unique=True, index=True)
    plan: str = "starter"
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    slack_webhook_url: Optional[str] = None
    discord_webhook_url: Optional[str] = None
    notify_email: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class Asset(SQLModel, table=True):
    __tablename__ = "assets"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    customer_id: str = Field(index=True)
    kind: str
    value: str
    verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Scan(SQLModel, table=True):
    __tablename__ = "scans"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    customer_id: str = Field(index=True)
    asset_id: str = Field(index=True)
    scan_type: str
    plugin: str
    status: str = "queued"
    parameters: Optional[dict] = Field(default={}, sa_column=Column(JSON))
    requires_approval: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class Finding(SQLModel, table=True):
    __tablename__ = "findings"
    __table_args__ = (
        UniqueConstraint("customer_id", "fingerprint", name="uq_finding_customer_fingerprint"),
    )

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    customer_id: str = Field(index=True)
    asset_id: str = Field(index=True)
    scan_id: str = Field(index=True)
    fingerprint: str = Field(index=True)
    title: str
    description: str
    severity: str
    status: str = "open"
    finding_type: str
    cvss_score: Optional[float] = None
    cve_id: Optional[str] = None
    cwe_id: Optional[str] = None
    affected_resource: Optional[str] = None
    proof_of_concept: Optional[str] = None
    remediation: Optional[str] = None
    references: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))
    tags: Optional[List[str]] = Field(default=[], sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None


class ScanResult(SQLModel, table=True):
    __tablename__ = "scan_results"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    scan_id: str = Field(index=True)
    raw_output: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
