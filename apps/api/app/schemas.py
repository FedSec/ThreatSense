from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, EmailStr, field_serializer, field_validator


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company_name: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    email: str
    full_name: str
    customer_id: str
    is_admin: bool
    plan: Optional[str] = None
    company_name: Optional[str] = None


class AssetCreate(BaseModel):
    kind: str
    value: str


class AssetOut(BaseModel):
    id: str
    kind: str
    value: str
    verified: bool
    customer_id: str


class ScanCreate(BaseModel):
    asset_id: str
    scan_type: str
    plugin: str
    requires_approval: bool = False
    parameters: Optional[Dict[str, Any]] = {}


class ScanOut(BaseModel):
    id: str
    asset_id: str
    scan_type: str
    plugin: str
    status: str
    parameters: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    @field_serializer("created_at", "updated_at", "started_at", "completed_at")
    def ser_dt(self, v: Optional[datetime]):
        return v.isoformat() if v else None


class FindingCreate(BaseModel):
    title: str
    description: str
    severity: str
    finding_type: str
    asset_id: str
    scan_id: str
    cvss_score: Optional[float] = None
    cve_id: Optional[str] = None
    cwe_id: Optional[str] = None
    affected_resource: Optional[str] = None
    proof_of_concept: Optional[str] = None
    remediation: Optional[str] = None
    references: Optional[List[str]] = []
    tags: Optional[List[str]] = []


class FindingUpdate(BaseModel):
    status: Optional[str] = None


class FindingOut(BaseModel):
    id: str
    customer_id: str
    asset_id: str
    scan_id: str
    fingerprint: str
    title: str
    description: str
    severity: str
    status: str
    finding_type: str
    cvss_score: Optional[float] = None
    cve_id: Optional[str] = None
    cwe_id: Optional[str] = None
    affected_resource: Optional[str] = None
    proof_of_concept: Optional[str] = None
    remediation: Optional[str] = None
    references: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None

    @field_serializer("created_at", "updated_at", "resolved_at")
    def ser_dt(self, v: Optional[datetime]):
        return v.isoformat() if v else None


class FindingStats(BaseModel):
    total: int
    critical: int
    high: int
    medium: int
    low: int
    info: int
    open: int
    resolved: int
    in_progress: int


class FindingAggregate(BaseModel):
    by_severity: Dict[str, int]
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    by_asset: Dict[str, int]


class CustomerUpdate(BaseModel):
    notify_email: Optional[EmailStr] = None
    notify_channel: Optional[Literal["email", "telegram"]] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    telegram_api_url: Optional[str] = None
    slack_webhook_url: Optional[str] = None
    discord_webhook_url: Optional[str] = None
    company_name: Optional[str] = None

    @field_validator(
        "notify_email",
        "telegram_bot_token",
        "telegram_chat_id",
        "telegram_api_url",
        mode="before",
    )
    @classmethod
    def empty_str_to_none(cls, v: object) -> object:
        if isinstance(v, str) and not v.strip():
            return None
        return v


class CustomerOut(BaseModel):
    id: str
    company_name: str
    email: str
    plan: str
    notify_email: Optional[str] = None
    notify_channel: str = "email"
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    telegram_api_url: str = "https://api.telegram.org"
    slack_webhook_url: Optional[str] = None
    discord_webhook_url: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None


class CheckoutRequest(BaseModel):
    plan: str  # starter | professional | enterprise
