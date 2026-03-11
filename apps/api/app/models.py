from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


# Enums
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


# Models
class Customer(SQLModel, table=True):
    __tablename__ = "customers"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    company_name: str
    email: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    # Relationships
    users: List["User"] = Relationship(back_populates="customer")
    assets: List["Asset"] = Relationship(back_populates="customer")


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str
    customer_id: str = Field(foreign_key="customers.id")
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    customer: Customer = Relationship(back_populates="users")


class Asset(SQLModel, table=True):
    __tablename__ = "assets"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    customer_id: str = Field(foreign_key="customers.id", index=True)
    kind: str  # domain, ip, host, webapp, log_source, url
    value: str
    verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    customer: Customer = Relationship(back_populates="assets")
    scans: List["Scan"] = Relationship(back_populates="asset")
    findings: List["Finding"] = Relationship(back_populates="asset")


class Scan(SQLModel, table=True):
    __tablename__ = "scans"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    asset_id: str = Field(foreign_key="assets.id", index=True)
    scan_type: str  # vuln_scan, soc, ptaas
    plugin: str  # nuclei_scan, nmap_stub, etc.
    status: str = ScanStatus.QUEUED  # queued, running, completed, failed, awaiting_approval
    parameters: dict = Field(default={}, sa_column_kwargs={"type_": "JSON"})
    requires_approval: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    # Relationships
    asset: Asset = Relationship(back_populates="scans")
    findings: List["Finding"] = Relationship(back_populates="scan")


class Finding(SQLModel, table=True):
    __tablename__ = "findings"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    asset_id: str = Field(foreign_key="assets.id", index=True)
    scan_id: str = Field(foreign_key="scans.id", index=True)

    # Core fields
    title: str
    description: str
    severity: str  # critical, high, medium, low, info
    status: str = FindingStatus.OPEN  # open, in_progress, resolved, false_positive, accepted_risk
    finding_type: str  # vulnerability, misconfiguration, etc.

    # Technical details
    cvss_score: Optional[float] = None
    cve_id: Optional[str] = None
    cwe_id: Optional[str] = None
    affected_resource: Optional[str] = None
    proof_of_concept: Optional[str] = None
    remediation: Optional[str] = None

    # Metadata
    references: List[str] = Field(default=[], sa_column_kwargs={"type_": "JSON"})
    tags: List[str] = Field(default=[], sa_column_kwargs={"type_": "JSON"})

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None

    # Relationships
    asset: Asset = Relationship(back_populates="findings")
    scan: Scan = Relationship(back_populates="findings")


class ScanResult(SQLModel, table=True):
    """Raw scan results from tools like Nuclei"""
    __tablename__ = "scan_results"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    scan_id: str = Field(foreign_key="scans.id", index=True)
    raw_output: dict = Field(sa_column_kwargs={"type_": "JSON"})
    created_at: datetime = Field(default_factory=datetime.utcnow)
