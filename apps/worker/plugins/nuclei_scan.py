import json
import os
import shutil
import subprocess
from datetime import datetime
from typing import Any

from plugins.base import BasePlugin, PluginResult


class NucleiScan(BasePlugin):
    """Nuclei-based vulnerability scanner plugin."""

    name = "nuclei_scan"

    def run(self, asset_kind: str, asset_value: str, params: dict[str, Any]) -> PluginResult:
        if not self._nuclei_exists():
            return PluginResult(
                findings=[{
                    "title": "Nuclei binary not installed in worker image",
                    "severity": "high",
                    "category": "scanner_error",
                    "evidence": "The 'nuclei' executable was not found on PATH.",
                    "remediation": "Install ProjectDiscovery nuclei and templates in the worker container.",
                }],
                artifact_path=None,
            )

        target = self._coerce_target(asset_kind, asset_value, params)
        severities = params.get("severities") or ["medium", "high", "critical"]
        if isinstance(severities, str):
            severities = [s.strip() for s in severities.split(",") if s.strip()]
        tags = params.get("tags")
        exclude_tags = params.get("exclude_tags") or "dos,fuzz"
        rate_limit = int(params.get("rate_limit") or 50)
        timeout = int(params.get("timeout") or 10)
        retries = int(params.get("retries") or 1)
        templates_dir = params.get("templates_dir") or "/opt/nuclei-templates"
        headless = bool(params.get("headless") or False)

        artifacts_root = params.get("artifacts_dir") or "/tmp/threatsense_artifacts"
        os.makedirs(artifacts_root, exist_ok=True)
        run_id = params.get("run_id") or datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        out_path = os.path.join(artifacts_root, f"nuclei_{run_id}.jsonl")

        cmd = [
            "nuclei",
            "-u", target,
            "-jsonl",
            "-o", out_path,
            "-severity", ",".join(severities),
            "-rl", str(rate_limit),
            "-timeout", str(timeout),
            "-retries", str(retries),
            "-silent",
        ]
        if templates_dir and os.path.isdir(templates_dir):
            cmd += ["-t", templates_dir]
        if tags:
            cmd += ["-tags", str(tags)]
        if exclude_tags:
            cmd += ["-exclude-tags", str(exclude_tags)]
        if headless:
            cmd += ["-headless"]

        wall_clock_timeout = int(params.get("wall_clock_timeout") or 600)

        try:
            subprocess.run(
                cmd,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=wall_clock_timeout,
            )
        except subprocess.TimeoutExpired:
            return PluginResult(
                findings=[{
                    "title": "Nuclei scan timed out",
                    "severity": "medium",
                    "category": "scanner_error",
                    "evidence": f"Scan exceeded wall_clock_timeout={wall_clock_timeout}s for target={target}.",
                    "remediation": "Reduce scope or increase wall_clock_timeout cautiously.",
                }],
                artifact_path=out_path if os.path.exists(out_path) else None,
            )
        except Exception as e:
            return PluginResult(
                findings=[{
                    "title": "Nuclei scan execution error",
                    "severity": "high",
                    "category": "scanner_error",
                    "evidence": f"{type(e).__name__}: {e}",
                    "remediation": "Check worker container logs and nuclei installation.",
                }],
                artifact_path=out_path if os.path.exists(out_path) else None,
            )

        findings = self._parse_jsonl(out_path)
        if not findings and not os.path.exists(out_path):
            findings = [{
                "title": "Nuclei produced no output",
                "severity": "info",
                "category": "scanner_error",
                "evidence": f"No results file for target={target}",
                "remediation": "Verify target reachability and template path.",
            }]
        return PluginResult(findings=findings, artifact_path=out_path if os.path.exists(out_path) else None)

    def _parse_jsonl(self, path: str) -> list[dict]:
        findings: list[dict] = []
        if not os.path.exists(path):
            return findings
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    raw = json.loads(line)
                except json.JSONDecodeError:
                    continue
                findings.append(self._map_result(raw))
        return findings

    def _map_result(self, raw: dict) -> dict:
        info = raw.get("info") or {}
        classification = info.get("classification") or {}
        cves = classification.get("cve-id") or classification.get("cve_id") or []
        cve_id = None
        if isinstance(cves, list) and cves:
            cve_id = cves[0]
        elif isinstance(cves, str):
            cve_id = cves

        refs = info.get("reference") or []
        if isinstance(refs, str):
            refs = [refs]

        tags = info.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        return {
            "title": info.get("name") or raw.get("template-id") or "Nuclei finding",
            "severity": (info.get("severity") or "info").lower(),
            "description": info.get("description") or "",
            "evidence": raw.get("matched-at") or raw.get("host") or "",
            "affected_resource": raw.get("matched-at") or raw.get("host") or raw.get("url"),
            "remediation": info.get("remediation") or "",
            "cve_id": cve_id,
            "cvss_score": classification.get("cvss-score") or classification.get("cvss_score"),
            "cwe_id": (classification.get("cwe-id") or [None])[0]
            if isinstance(classification.get("cwe-id"), list)
            else classification.get("cwe-id"),
            "references": refs,
            "tags": tags,
            "finding_type": "vulnerability",
            "info": info,
        }

    def _coerce_target(self, asset_kind: str, asset_value: str, params: dict) -> str:
        if params.get("target_url"):
            return str(params["target_url"])
        value = (asset_value or "").strip()
        kind = (asset_kind or "").lower()
        if value.startswith("http://") or value.startswith("https://"):
            return value
        if kind in ("url", "webapp", "domain", "host"):
            return f"https://{value}"
        if kind == "ip":
            return f"http://{value}"
        return value

    def _nuclei_exists(self) -> bool:
        return shutil.which("nuclei") is not None
