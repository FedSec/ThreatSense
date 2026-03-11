from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/findings", tags=["findings"])

# Enums for findings
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

# Models
class FindingBase(BaseModel):
    title: str
    description: str
    severity: Severity
    finding_type: FindingType
    asset_id: str
    scan_id: str

class FindingCreate(FindingBase):
    cvss_score: Optional[float] = None
    cve_id: Optional[str] = None
    cwe_id: Optional[str] = None
    affected_resource: Optional[str] = None
    proof_of_concept: Optional[str] = None
    remediation: Optional[str] = None
    references: Optional[List[str]] = []
    tags: Optional[List[str]] = []

class Finding(FindingCreate):
    id: str
    status: FindingStatus
    created_at: str
    updated_at: str
    resolved_at: Optional[str] = None
    resolved_by: Optional[str] = None

class FindingUpdate(BaseModel):
    status: Optional[FindingStatus] = None
    notes: Optional[str] = None

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

# Mock database
MOCK_FINDINGS_DB: List[Finding] = []

# Helper function to create sample findings for demo
def seed_demo_findings(asset_id: str, scan_id: str):
    """Create realistic penetration testing findings"""
    demo_findings = [
        {
            "title": "SQL Injection Vulnerability in Login Form",
            "description": "The login form is vulnerable to SQL injection attacks. Unauthenticated attackers can bypass authentication and gain administrative access to the database.",
            "severity": Severity.CRITICAL,
            "finding_type": FindingType.VULNERABILITY,
            "cvss_score": 9.8,
            "cve_id": "CVE-2024-12345",
            "cwe_id": "CWE-89",
            "affected_resource": "/api/auth/login",
            "proof_of_concept": "' OR '1'='1' -- ",
            "remediation": "Use parameterized queries or prepared statements. Implement input validation and sanitization. Apply the principle of least privilege for database accounts.",
            "references": [
                "https://owasp.org/www-community/attacks/SQL_Injection",
                "https://cwe.mitre.org/data/definitions/89.html"
            ],
            "tags": ["sqli", "authentication", "database", "owasp-top-10"]
        },
        {
            "title": "Cross-Site Scripting (XSS) in User Profile",
            "description": "Stored XSS vulnerability allows attackers to inject malicious scripts that execute when other users view the profile page.",
            "severity": Severity.HIGH,
            "finding_type": FindingType.VULNERABILITY,
            "cvss_score": 7.3,
            "cwe_id": "CWE-79",
            "affected_resource": "/profile/edit",
            "proof_of_concept": "<script>alert(document.cookie)</script>",
            "remediation": "Implement proper output encoding/escaping. Use Content Security Policy headers. Validate and sanitize all user inputs.",
            "references": [
                "https://owasp.org/www-community/attacks/xss/",
                "https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html"
            ],
            "tags": ["xss", "stored-xss", "client-side", "owasp-top-10"]
        },
        {
            "title": "Sensitive Data Exposure via API",
            "description": "User API endpoint returns sensitive information including password hashes and internal IDs without proper authentication.",
            "severity": Severity.HIGH,
            "finding_type": FindingType.VULNERABILITY,
            "cvss_score": 7.5,
            "cwe_id": "CWE-200",
            "affected_resource": "/api/users/list",
            "proof_of_concept": "GET /api/users/list returns: {users: [{password_hash: 'xxx', ssn: '123-45-6789'}]}",
            "remediation": "Implement proper authentication and authorization. Remove sensitive fields from API responses. Use field-level access control.",
            "references": [
                "https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure"
            ],
            "tags": ["data-exposure", "api", "authentication"]
        },
        {
            "title": "Broken Access Control - IDOR Vulnerability",
            "description": "Insecure Direct Object Reference allows users to access other users' data by manipulating the ID parameter.",
            "severity": Severity.HIGH,
            "finding_type": FindingType.VULNERABILITY,
            "cvss_score": 8.1,
            "cwe_id": "CWE-639",
            "affected_resource": "/api/invoices/{id}",
            "proof_of_concept": "Change invoice ID from 1001 to 1002 to view another user's invoice",
            "remediation": "Implement proper authorization checks. Use indirect references or UUIDs. Validate user permissions before returning data.",
            "references": [
                "https://owasp.org/www-project-top-ten/2017/A5_2017-Broken_Access_Control"
            ],
            "tags": ["idor", "authorization", "access-control", "owasp-top-10"]
        },
        {
            "title": "Missing HTTPS Enforcement",
            "description": "Application allows connections over HTTP, exposing sensitive data to man-in-the-middle attacks.",
            "severity": Severity.MEDIUM,
            "finding_type": FindingType.MISCONFIGURATION,
            "cvss_score": 5.9,
            "affected_resource": "http://example.com",
            "remediation": "Enforce HTTPS for all connections. Implement HSTS headers. Redirect all HTTP traffic to HTTPS.",
            "references": [
                "https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Protection_Cheat_Sheet.html"
            ],
            "tags": ["https", "tls", "mitm", "transport-security"]
        },
        {
            "title": "Weak Password Policy",
            "description": "Password policy allows weak passwords (minimum 6 characters, no complexity requirements).",
            "severity": Severity.MEDIUM,
            "finding_type": FindingType.WEAK_CREDENTIAL,
            "cvss_score": 5.3,
            "affected_resource": "/auth/register",
            "remediation": "Enforce strong password requirements (minimum 12 characters, complexity). Implement password strength meter. Consider multi-factor authentication.",
            "references": [
                "https://pages.nist.gov/800-63-3/sp800-63b.html"
            ],
            "tags": ["password", "authentication", "credential"]
        },
        {
            "title": "Outdated jQuery Version (3.3.1)",
            "description": "Application uses jQuery 3.3.1 which contains known security vulnerabilities.",
            "severity": Severity.MEDIUM,
            "finding_type": FindingType.VULNERABILITY,
            "cvss_score": 6.1,
            "cve_id": "CVE-2020-11022",
            "cwe_id": "CWE-79",
            "affected_resource": "/static/js/jquery-3.3.1.min.js",
            "remediation": "Update jQuery to version 3.6.0 or later. Review and update all third-party dependencies regularly.",
            "references": [
                "https://blog.jquery.com/2020/04/10/jquery-3-5-0-released/",
                "https://nvd.nist.gov/vuln/detail/CVE-2020-11022"
            ],
            "tags": ["dependency", "cve", "jquery", "xss"]
        },
        {
            "title": "Missing Security Headers",
            "description": "Application is missing critical security headers including X-Frame-Options, X-Content-Type-Options, and Content-Security-Policy.",
            "severity": Severity.LOW,
            "finding_type": FindingType.MISCONFIGURATION,
            "cvss_score": 4.3,
            "affected_resource": "All pages",
            "remediation": "Implement security headers: X-Frame-Options: DENY, X-Content-Type-Options: nosniff, Content-Security-Policy with appropriate directives.",
            "references": [
                "https://owasp.org/www-project-secure-headers/"
            ],
            "tags": ["headers", "security-headers", "hardening"]
        },
        {
            "title": "Information Disclosure in Error Messages",
            "description": "Detailed error messages expose internal system information including file paths and database structure.",
            "severity": Severity.LOW,
            "finding_type": FindingType.VULNERABILITY,
            "cvss_score": 3.7,
            "cwe_id": "CWE-209",
            "affected_resource": "/api/*",
            "remediation": "Implement generic error messages for users. Log detailed errors server-side only. Use custom error pages.",
            "references": [
                "https://owasp.org/www-community/Improper_Error_Handling"
            ],
            "tags": ["information-disclosure", "error-handling"]
        },
        {
            "title": "Exposed .git Directory",
            "description": "The .git directory is accessible via web browser, potentially exposing source code and sensitive configuration.",
            "severity": Severity.HIGH,
            "finding_type": FindingType.MISCONFIGURATION,
            "cvss_score": 7.5,
            "affected_resource": "/.git/",
            "proof_of_concept": "curl http://example.com/.git/config returns git configuration",
            "remediation": "Block access to .git directories in web server configuration. Remove .git from production deployments.",
            "references": [
                "https://en.internetwache.org/dont-publicly-expose-git-or-how-we-downloaded-your-websites-sourcecode-an-analysis-of-alexas-1m-28-07-2015/"
            ],
            "tags": ["misconfiguration", "source-code", "exposure"]
        }
    ]

    for idx, finding_data in enumerate(demo_findings):
        now = datetime.utcnow().isoformat()
        finding = Finding(
            id=str(uuid.uuid4()),
            asset_id=asset_id,
            scan_id=scan_id,
            status=FindingStatus.OPEN if idx < 7 else (FindingStatus.RESOLVED if idx < 9 else FindingStatus.IN_PROGRESS),
            created_at=now,
            updated_at=now,
            resolved_at=None if idx < 7 else now,
            **finding_data
        )
        MOCK_FINDINGS_DB.append(finding)

@router.get("", response_model=List[Finding])
async def list_findings(
    severity: Optional[Severity] = None,
    status: Optional[FindingStatus] = None,
    asset_id: Optional[str] = None,
    scan_id: Optional[str] = None,
    finding_type: Optional[FindingType] = None,
    limit: int = Query(100, le=1000)
):
    """List findings with optional filters"""
    results = MOCK_FINDINGS_DB.copy()

    if severity:
        results = [f for f in results if f.severity == severity]
    if status:
        results = [f for f in results if f.status == status]
    if asset_id:
        results = [f for f in results if f.asset_id == asset_id]
    if scan_id:
        results = [f for f in results if f.scan_id == scan_id]
    if finding_type:
        results = [f for f in results if f.finding_type == finding_type]

    # Sort by severity (critical first) and then by created_at
    severity_order = {
        Severity.CRITICAL: 0,
        Severity.HIGH: 1,
        Severity.MEDIUM: 2,
        Severity.LOW: 3,
        Severity.INFO: 4
    }
    results.sort(key=lambda x: (severity_order.get(x.severity, 99), x.created_at), reverse=True)

    return results[:limit]

@router.get("/stats", response_model=FindingStats)
async def get_finding_stats():
    """Get statistics about findings"""
    total = len(MOCK_FINDINGS_DB)

    stats = FindingStats(
        total=total,
        critical=len([f for f in MOCK_FINDINGS_DB if f.severity == Severity.CRITICAL]),
        high=len([f for f in MOCK_FINDINGS_DB if f.severity == Severity.HIGH]),
        medium=len([f for f in MOCK_FINDINGS_DB if f.severity == Severity.MEDIUM]),
        low=len([f for f in MOCK_FINDINGS_DB if f.severity == Severity.LOW]),
        info=len([f for f in MOCK_FINDINGS_DB if f.severity == Severity.INFO]),
        open=len([f for f in MOCK_FINDINGS_DB if f.status == FindingStatus.OPEN]),
        resolved=len([f for f in MOCK_FINDINGS_DB if f.status == FindingStatus.RESOLVED]),
        in_progress=len([f for f in MOCK_FINDINGS_DB if f.status == FindingStatus.IN_PROGRESS])
    )

    return stats

@router.post("", response_model=Finding)
async def create_finding(finding: FindingCreate):
    """Create a new finding"""
    now = datetime.utcnow().isoformat()

    new_finding = Finding(
        id=str(uuid.uuid4()),
        **finding.dict(),
        status=FindingStatus.OPEN,
        created_at=now,
        updated_at=now
    )

    MOCK_FINDINGS_DB.append(new_finding)
    return new_finding

@router.get("/{finding_id}", response_model=Finding)
async def get_finding(finding_id: str):
    """Get a specific finding by ID"""
    for finding in MOCK_FINDINGS_DB:
        if finding.id == finding_id:
            return finding
    raise HTTPException(status_code=404, detail="Finding not found")

@router.patch("/{finding_id}", response_model=Finding)
async def update_finding(finding_id: str, update: FindingUpdate):
    """Update a finding's status or add notes"""
    for finding in MOCK_FINDINGS_DB:
        if finding.id == finding_id:
            if update.status:
                finding.status = update.status
                if update.status == FindingStatus.RESOLVED:
                    finding.resolved_at = datetime.utcnow().isoformat()
                    finding.resolved_by = "current_user"  # TODO: Get from auth

            finding.updated_at = datetime.utcnow().isoformat()
            return finding

    raise HTTPException(status_code=404, detail="Finding not found")

@router.delete("/{finding_id}")
async def delete_finding(finding_id: str):
    """Delete a finding (mark as false positive)"""
    for i, finding in enumerate(MOCK_FINDINGS_DB):
        if finding.id == finding_id:
            MOCK_FINDINGS_DB[i].status = FindingStatus.FALSE_POSITIVE
            MOCK_FINDINGS_DB[i].updated_at = datetime.utcnow().isoformat()
            return {"message": "Finding marked as false positive"}

    raise HTTPException(status_code=404, detail="Finding not found")

@router.post("/seed-demo")
async def seed_demo_data(asset_id: str, scan_id: str):
    """Seed demo findings for testing (remove in production)"""
    seed_demo_findings(asset_id, scan_id)
    return {"message": f"Created {len(MOCK_FINDINGS_DB)} demo findings"}

@router.get("/export/json")
async def export_findings_json(
    severity: Optional[Severity] = None,
    status: Optional[FindingStatus] = None
):
    """Export findings as JSON"""
    findings = await list_findings(severity=severity, status=status)
    return {"findings": findings, "exported_at": datetime.utcnow().isoformat()}

@router.get("/export/csv")
async def export_findings_csv():
    """Export findings as CSV format"""
    import io
    import csv

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "ID", "Title", "Severity", "Status", "Type", "CVSS Score",
        "CVE ID", "CWE ID", "Asset ID", "Scan ID", "Created", "Resolved"
    ])

    # Data
    for finding in MOCK_FINDINGS_DB:
        writer.writerow([
            finding.id,
            finding.title,
            finding.severity,
            finding.status,
            finding.finding_type,
            finding.cvss_score or "N/A",
            finding.cve_id or "N/A",
            finding.cwe_id or "N/A",
            finding.asset_id,
            finding.scan_id,
            finding.created_at,
            finding.resolved_at or "N/A"
        ])

    return {"csv": output.getvalue(), "exported_at": datetime.utcnow().isoformat()}
