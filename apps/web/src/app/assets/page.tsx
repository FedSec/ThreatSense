"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import Navigation from "@/components/Navigation";
import { colors, styles } from "@/styles/theme";

type Asset = {
  id: string;
  kind: string;
  value: string;
  verified: boolean;
};

const NUCLEI_PRESETS: Record<string, any> = {
  "Default (Med+)": {
    severities: ["medium", "high", "critical"],
    exclude_tags: "dos,fuzz",
    rate_limit: 50,
    timeout: 10,
    retries: 1,
    wall_clock_timeout: 600,
    headless: false,
  },
  "Quick (High/Critical)": {
    severities: ["high", "critical"],
    exclude_tags: "dos,fuzz",
    rate_limit: 75,
    timeout: 8,
    retries: 1,
    wall_clock_timeout: 420,
    headless: false,
  },
  "CVE Focus": {
    severities: ["medium", "high", "critical"],
    tags: "cves",
    exclude_tags: "dos,fuzz",
    rate_limit: 40,
    timeout: 12,
    retries: 1,
    wall_clock_timeout: 900,
    headless: false,
  },
};

function safeJsonParse(input: string) {
  if (!input.trim()) return {};
  try {
    return JSON.parse(input);
  } catch {
    throw new Error('Parameters must be valid JSON (example: {"timeout":10}).');
  }
}

export default function AssetsPage() {
  const [token, setToken] = useState("");
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  const [assets, setAssets] = useState<Asset[]>([]);

  // Create asset form
  const [kind, setKind] = useState("domain");
  const [value, setValue] = useState("");

  // Default scan settings
  const [presetKey, setPresetKey] = useState<keyof typeof NUCLEI_PRESETS>("Default (Med+)");
  const [scanType, setScanType] = useState("vuln_scan");
  const [plugin, setPlugin] = useState("nuclei_scan");
  const [paramsText, setParamsText] = useState(
    JSON.stringify(NUCLEI_PRESETS["Default (Med+)"], null, 2)
  );

  async function loadAssets(t: string) {
    setErr("");
    setLoading(true);
    try {
      const a = await apiFetch("/assets", {}, t);
      setAssets(a);
    } catch (e: any) {
      setErr(e?.message || "Failed to load assets.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const t = localStorage.getItem("ts_token") || "";
    if (!t) {
      window.location.href = "/login";
      return;
    }
    setToken(t);
    loadAssets(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function createAsset() {
    setErr("");
    setSuccessMsg("");
    try {
      if (!value.trim()) throw new Error("Asset value is required (ex: example.com).");

      await apiFetch(
        "/assets",
        {
          method: "POST",
          body: JSON.stringify({ kind, value: value.trim() }),
        },
        token
      );

      setValue("");
      setSuccessMsg(`Asset "${value.trim()}" created successfully!`);
      await loadAssets(token);
    } catch (e: any) {
      setErr(e?.message || "Failed to create asset.");
    }
  }

  async function startScan(assetId: string, assetValue: string) {
    setErr("");
    setSuccessMsg("");
    try {
      const parameters = safeJsonParse(paramsText);

      await apiFetch(
        "/scans",
        {
          method: "POST",
          body: JSON.stringify({
            asset_id: assetId,
            scan_type: scanType,
            plugin,
            requires_approval: false,
            parameters,
          }),
        },
        token
      );

      setSuccessMsg(`Scan queued for ${assetValue}!`);
    } catch (e: any) {
      setErr(e?.message || "Failed to start scan.");
    }
  }

  return (
    <main style={{ ...styles.container, position: "relative", minHeight: "100vh" }}>
      <div className="scanner-line" />

      <Navigation />

      <h1 style={{
        fontSize: "40px",
        margin: 0,
        marginBottom: "12px",
        color: colors.textPrimary,
        fontWeight: 700,
      }}>
        Assets
      </h1>
      <p style={{
        marginTop: 0,
        marginBottom: "32px",
        color: colors.textSecondary,
        fontSize: "16px",
      }}>
        Manage your attack surface - domains, IPs, web apps, and log sources
      </p>

      {err && (
        <div style={{ ...styles.alert, ...styles.alertError }}>
          <strong>Error:</strong> {err}
        </div>
      )}

      {successMsg && (
        <div style={{ ...styles.alert, ...styles.alertSuccess }}>
          <strong>Success:</strong> {successMsg}
        </div>
      )}

      {/* Add Asset Section */}
      <section style={{ ...styles.cardGlow, marginBottom: "32px" }}>
        <h2 style={{
          margin: 0,
          marginBottom: "8px",
          color: colors.primary,
          fontSize: "24px",
          fontWeight: 600,
        }}>
          Add New Asset
        </h2>
        <p style={{
          marginTop: 0,
          marginBottom: "24px",
          color: colors.textSecondary,
          fontSize: "14px",
        }}>
          Add a target for scanning: domain, IP, host, webapp, log source, or URL
        </p>

        <div style={{
          display: "grid",
          gridTemplateColumns: "180px 1fr 180px",
          gap: "12px",
        }}>
          <div>
            <label style={styles.label}>Type</label>
            <select
              style={styles.select}
              value={kind}
              onChange={(e) => setKind(e.target.value)}
            >
              <option value="domain">Domain</option>
              <option value="ip">IP Address</option>
              <option value="host">Host</option>
              <option value="webapp">Web App</option>
              <option value="log_source">Log Source</option>
              <option value="url">URL</option>
            </select>
          </div>

          <div>
            <label style={styles.label}>Value</label>
            <input
              style={styles.input}
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder="example.com or https://example.com"
              onKeyPress={(e) => e.key === "Enter" && createAsset()}
            />
          </div>

          <div>
            <label style={styles.label}>&nbsp;</label>
            <button
              style={{ ...styles.button, width: "100%" }}
              onClick={createAsset}
            >
              CREATE
            </button>
          </div>
        </div>
      </section>

      {/* Default Scan Settings */}
      <section style={{ ...styles.card, marginBottom: "32px" }}>
        <h2 style={{
          margin: 0,
          marginBottom: "8px",
          color: colors.primary,
          fontSize: "24px",
          fontWeight: 600,
        }}>
          Default Scan Settings
        </h2>
        <p style={{
          marginTop: 0,
          marginBottom: "24px",
          color: colors.textSecondary,
          fontSize: "14px",
        }}>
          Configure default parameters for quick scanning from the asset list
        </p>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(350px, 1fr))",
          gap: "24px",
        }}>
          <div>
            <label style={styles.label}>Scan Type</label>
            <select
              style={styles.select}
              value={scanType}
              onChange={(e) => setScanType(e.target.value)}
            >
              <option value="vuln_scan">Vulnerability Scan</option>
              <option value="soc">SOC Detection Run</option>
              <option value="ptaas">PTaaS Workflow</option>
            </select>

            <label style={{ ...styles.label, marginTop: "16px" }}>Nuclei Preset</label>
            <select
              style={styles.select}
              value={presetKey as string}
              onChange={(e) => {
                const key = e.target.value as keyof typeof NUCLEI_PRESETS;
                setPresetKey(key);
                setParamsText(JSON.stringify(NUCLEI_PRESETS[key], null, 2));
                setPlugin("nuclei_scan");
                setScanType("vuln_scan");
              }}
            >
              {Object.keys(NUCLEI_PRESETS).map((k) => (
                <option key={k} value={k}>
                  {k}
                </option>
              ))}
            </select>

            <label style={{ ...styles.label, marginTop: "16px" }}>Plugin</label>
            <input
              style={styles.input}
              value={plugin}
              onChange={(e) => setPlugin(e.target.value)}
              placeholder='nuclei_scan'
            />
          </div>

          <div>
            <label style={styles.label}>Parameters (JSON)</label>
            <textarea
              style={{ ...styles.textarea, height: "170px" }}
              value={paramsText}
              onChange={(e) => setParamsText(e.target.value)}
            />
          </div>
        </div>
      </section>

      {/* Assets List */}
      <section style={styles.card}>
        <h2 style={{
          marginBottom: "20px",
          color: colors.primary,
          fontSize: "24px",
          fontWeight: 600,
        }}>
          All Assets
        </h2>

        {loading ? (
          <div style={{ color: colors.textSecondary, padding: "20px", textAlign: "center" }}>
            Loading assets...
          </div>
        ) : assets.length === 0 ? (
          <div style={{ color: colors.textMuted, padding: "20px", textAlign: "center" }}>
            No assets yet. Add your first asset above to get started!
          </div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.tableHeader}>Type</th>
                  <th style={styles.tableHeader}>Value</th>
                  <th style={styles.tableHeader}>Verified</th>
                  <th style={styles.tableHeader}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {assets.map((a) => (
                  <tr key={a.id}>
                    <td style={styles.tableCell}>
                      <span style={{
                        textTransform: "uppercase",
                        fontSize: "12px",
                        fontWeight: 600,
                        color: colors.primary,
                      }}>
                        {a.kind}
                      </span>
                    </td>
                    <td style={styles.tableCell}>{a.value}</td>
                    <td style={styles.tableCell}>
                      <span style={{
                        color: a.verified ? colors.success : colors.textMuted,
                        fontSize: "12px",
                        fontWeight: 600,
                      }}>
                        {a.verified ? "✓ VERIFIED" : "UNVERIFIED"}
                      </span>
                    </td>
                    <td style={styles.tableCell}>
                      <button
                        style={{
                          ...styles.button,
                          padding: "8px 16px",
                          fontSize: "12px",
                        }}
                        onClick={() => startScan(a.id, a.value)}
                      >
                        START SCAN
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <button
        style={{ ...styles.buttonSecondary, marginTop: "24px" }}
        onClick={() => loadAssets(token)}
        disabled={loading}
      >
        REFRESH ASSETS
      </button>
    </main>
  );
}
