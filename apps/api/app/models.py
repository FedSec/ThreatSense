from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON, UniqueConstraint
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    ACCEPTED_RISK = "accepted_risk"


class FindingType(str, Enum):
    VULNERABILITY = "vulnerability"
    MISCONFIGURATION = "misconfiguration"
    WEAK_CREDENTIAL = "weak_credential"
    EXPOSED_SERVICE = "exposed_service"
    CVE = "cve"
    COMPLIANCE = "compliance"


class ScanStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    AWAITING_APPROVAL = "awaiting_approval"


class PlanTier(str, Enum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class Customer(SQLModel, table=True):
    __tablename__ = "customers"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    company_name: str
    email: str = Field(unique=True, index=True)
    plan: str = Field(default=PlanTier.STARTER.value)
    stripe_customer_id: Optional[str] = Field(default=None, index=True)
    stripe_subscription_id: Optional[str] = None
    slack_webhook_url: Optional[str] = None
    discord_webhook_url: Optional[str] = None
    notify_email: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    users: List["User"] = Relationship(back_populates="customer")
    assets: List["Asset"] = Relationship(back_populates="customer")


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    customer_id: str = Field(foreign_key="customers.id", index=True)
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    customer: Customer = Relationship(back_populates="users")


class Asset(SQLModel, table=True):
    __tablename__ = "assets"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    customer_id: str = Field(foreign_key="customers.id", index=True)
    kind: str
    value: str
    verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    customer: Customer = Relationship(back_populates="assets")
    scans: List["Scan"] = Relationship(back_populates="asset")
    findings: List["Finding"] = Relationship(back_populates="asset")


class Scan(SQLModel, table=True):
    __tablename__ = "scans"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    customer_id: str = Field(foreign_key="customers.id", index=True)
    asset_id: str = Field(foreign_key="assets.id", index=True)
    scan_type: str
    plugin: str
    status: str = ScanStatus.QUEUED.value
    parameters: Optional[dict] = Field(default={}, sa_column=Column(JSON))
    requires_approval: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    asset: Asset = Relationship(back_populates="scans")
    findings: List["Finding"] = Relationship(back_populates="scan")


class Finding(SQLModel, table=True):
    __tablename__ = "findings"
    __table_args__ = (
        UniqueConstraint("customer_id", "fingerprint", name="uq_finding_customer_fingerprint"),
    )

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    customer_id: str = Field(foreign_key="customers.id", index=True)
    asset_id: str = Field(foreign_key="assets.id", index=True)
    scan_id: str = Field(foreign_key="scans.id", index=True)
    fingerprint: str = Field(index=True)

    title: str
    description: str
    severity: str
    status: str = FindingStatus.OPEN.value
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

    asset: Asset = Relationship(back_populates="findings")
    scan: Scan = Relationship(back_populates="findings")


class ScanResult(SQLModel, table=True):
    __tablename__ = "scan_results"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    scan_id: str = Field(foreign_key="scans.id", index=True)
    raw_output: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
