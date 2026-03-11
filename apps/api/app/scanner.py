"""
Real Nuclei Scanner Integration

This module handles actual vulnerability scanning using Nuclei.
Install Nuclei: https://github.com/projectdiscovery/nuclei
"""

import subprocess
import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path


class NucleiScanner:
    def __init__(self):
        self.nuclei_path = self._find_nuclei()
        if not self.nuclei_path:
            print("⚠️  Nuclei not found. Install with: go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest")

    def _find_nuclei(self) -> Optional[str]:
        """Find Nuclei binary in PATH"""
        try:
            result = subprocess.run(
                ["which", "nuclei"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def is_available(self) -> bool:
        """Check if Nuclei is installed and available"""
        return self.nuclei_path is not None

    def scan(
        self,
        target: str,
        severities: List[str] = None,
        tags: List[str] = None,
        exclude_tags: List[str] = None,
        rate_limit: int = 150,
        timeout: int = 5,
        retries: int = 1
    ) -> Dict[str, Any]:
        """
        Run Nuclei scan against a target

        Args:
            target: URL or domain to scan
            severities: List of severities to include (critical, high, medium, low, info)
            tags: List of tags to include
            exclude_tags: List of tags to exclude
            rate_limit: Requests per second
            timeout: Timeout per request in seconds
            retries: Number of retries

        Returns:
            Dict with scan results and metadata
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Nuclei not installed",
                "results": []
            }

        # Build command
        cmd = [
            self.nuclei_path,
            "-target", target,
            "-json",  # JSON output
            "-silent",  # Suppress banner
            "-no-color",
            "-rate-limit", str(rate_limit),
            "-timeout", str(timeout),
            "-retries", str(retries),
        ]

        # Add severity filters
        if severities:
            cmd.extend(["-severity", ",".join(severities)])
        else:
            cmd.extend(["-severity", "critical,high,medium"])

        # Add tag filters
        if tags:
            cmd.extend(["-tags", ",".join(tags)])

        if exclude_tags:
            cmd.extend(["-exclude-tags", ",".join(exclude_tags)])

        try:
            # Run Nuclei
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout for scan
            )

            # Parse JSON output (one JSON object per line)
            findings = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            findings.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue

            return {
                "success": True,
                "target": target,
                "findings_count": len(findings),
                "results": findings,
                "raw_stdout": result.stdout,
                "raw_stderr": result.stderr
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Scan timed out after 10 minutes",
                "results": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": []
            }

    def parse_finding(self, nuclei_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Nuclei JSON output to ThreatSense finding format

        Nuclei output example:
        {
            "template-id": "cve-2021-12345",
            "info": {
                "name": "Vulnerability Name",
                "severity": "high",
                "description": "...",
                "reference": ["url1", "url2"],
                "tags": ["cve", "wp-plugin"]
            },
            "type": "http",
            "host": "https://example.com",
            "matched-at": "https://example.com/path",
            "curl-command": "...",
            ...
        }
        """
        info = nuclei_result.get("info", {})

        # Map Nuclei severity to our severity
        severity_map = {
            "critical": "critical",
            "high": "high",
            "medium": "medium",
            "low": "low",
            "info": "info",
            "unknown": "info"
        }

        severity = severity_map.get(
            info.get("severity", "unknown").lower(),
            "info"
        )

        # Extract CVE ID if present
        template_id = nuclei_result.get("template-id", "")
        cve_id = None
        if template_id.startswith("cve-"):
            cve_id = template_id.upper().replace("-", "-", 1)  # CVE-2021-12345

        # Build finding
        finding = {
            "title": info.get("name", template_id),
            "description": info.get("description", "No description available"),
            "severity": severity,
            "finding_type": "vulnerability",
            "cvss_score": None,  # Nuclei doesn't always provide CVSS
            "cve_id": cve_id,
            "cwe_id": None,  # Extract from tags if present
            "affected_resource": nuclei_result.get("matched-at") or nuclei_result.get("host"),
            "proof_of_concept": nuclei_result.get("curl-command", ""),
            "remediation": info.get("remediation", ""),
            "references": info.get("reference", []),
            "tags": info.get("tags", [])
        }

        # Try to extract CWE from tags
        for tag in finding["tags"]:
            if tag.startswith("cwe-"):
                finding["cwe_id"] = tag.upper()
                break

        return finding


class MockScanner:
    """
    Fallback scanner when Nuclei is not installed.
    Returns realistic test findings for demo purposes.
    """

    def is_available(self) -> bool:
        return True

    def scan(self, target: str, **kwargs) -> Dict[str, Any]:
        """Generate mock findings for testing"""
        from app.routers.findings import seed_demo_findings
        import uuid

        # This is a mock - in the actual worker, we'd create findings in the database
        return {
            "success": True,
            "target": target,
            "findings_count": 10,
            "results": [],  # Mock findings will be created by seed_demo_findings
            "note": "Using mock scanner. Install Nuclei for real scanning."
        }


# Global scanner instance
_scanner = None


def get_scanner():
    """Get scanner instance (Nuclei if available, mock otherwise)"""
    global _scanner
    if _scanner is None:
        nuclei = NucleiScanner()
        if nuclei.is_available():
            _scanner = nuclei
            print("✅ Using real Nuclei scanner")
        else:
            _scanner = MockScanner()
            print("⚠️  Using mock scanner (Nuclei not installed)")
    return _scanner
