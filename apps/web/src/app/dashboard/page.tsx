"use client";

import { useEffect, useMemo, useState } from "react";
import { apiFetch } from "@/lib/api";
import Navigation from "@/components/Navigation";
import { colors, styles } from "@/styles/theme";

type Asset = {
  id: string;
  kind: string;
  value: string;
  verified: boolean;
};

type Scan = {
  id: string;
  status: string;
  scan_type: string;
  plugin: string;
};

const SCAN_PRESETS: Record<string, { label: string; parameters: object }> = {
  default: {
    label: "Standard (Medium, High, Critical)",
    parameters: { severities: ["medium", "high", "critical"], rate_limit: 50, timeout: 10, retries: 2 },
  },
  critical_only: {
    label: "Quick (High & Critical only)",
    parameters: { severities: ["high", "critical"], rate_limit: 75, timeout: 8, retries: 2 },
  },
  cve_focus: {
    label: "CVE Focus",
    parameters: { severities: ["medium", "high", "critical"], tags: "cves", rate_limit: 40, timeout: 12, retries: 2 },
  },
};

export default function DashboardPage() {
  const [token, setToken] = useState("");
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  const [assets, setAssets] = useState<Asset[]>([]);
  const [scans, setScans] = useState<Scan[]>([]);

  // Quick scan form
  const [assetId, setAssetId] = useState("");
  const [preset, setPreset] = useState("default");

  const recentScans = useMemo(() => scans.slice(0, 10), [scans]);

  async function loadAll(t: string) {
    setErr("");
    setLoading(true);
    try {
      const [a, s] = await Promise.all([
        apiFetch("/assets", {}, t),
        apiFetch("/scans", {}, t),
      ]);
      setAssets(a);
      setScans(s);
      if (!assetId && a?.length) setAssetId(a[0].id);
    } catch (e: any) {
      setErr(e?.message || "Failed to load dashboard.");
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
    loadAll(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function startScan() {
    setErr("");
    try {
      if (!assetId) throw new Error("Select an asset first.");
      const { parameters } = SCAN_PRESETS[preset];

      await apiFetch(
        "/scans",
        {
          method: "POST",
          body: JSON.stringify({
            asset_id: assetId,
            scan_type: "vuln_scan",
            plugin: "nuclei_scan",
            requires_approval: false,
            parameters,
          }),
        },
        token
      );

      await loadAll(token);
    } catch (e: any) {
      setErr(e?.message || "Failed to start scan.");
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "completed": return colors.success;
      case "running": return colors.info;
      case "failed": return colors.error;
      case "queued": return colors.warning;
      case "awaiting_approval": return colors.medium;
      default: return colors.textSecondary;
    }
  };

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
        Dashboard
      </h1>
      <p style={{
        marginTop: 0,
        marginBottom: "32px",
        color: colors.textSecondary,
        fontSize: "16px",
      }}>
        Monitor your security posture and run automated scans
      </p>

      {err && (
        <div style={{ ...styles.alert, ...styles.alertError }}>
          <strong>Error:</strong> {err}
        </div>
      )}

      {/* Stat Cards */}
      <section style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
        gap: "20px",
        marginBottom: "32px",
      }}>
        <StatCard title="Total Assets" value={assets.length} />
        <StatCard title="Total Scans" value={scans.length} />
        <StatCard
          title="Active Scans"
          value={scans.filter(s => s.status === "running" || s.status === "queued").length}
        />
      </section>

      {/* Run Scan Section */}
      <section style={{ ...styles.cardGlow, marginBottom: "32px" }}>
        <h2 style={{
          margin: 0,
          marginBottom: "8px",
          color: colors.primary,
          fontSize: "24px",
          fontWeight: 600,
        }}>
          Run a Scan
        </h2>
        <p style={{
          marginTop: 0,
          marginBottom: "24px",
          color: colors.textSecondary,
          fontSize: "14px",
        }}>
          Start vulnerability scans, SOC detection runs, or PTaaS workflows against your assets
        </p>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
          gap: "16px",
          alignItems: "end",
        }}>
          <div>
            <label style={styles.label}>Asset</label>
            <select
              style={styles.select}
              value={assetId}
              onChange={(e) => setAssetId(e.target.value)}
            >
              <option value="">Select an asset…</option>
              {assets.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.kind}: {a.value}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label style={styles.label}>Scan Profile</label>
            <select
              style={styles.select}
              value={preset}
              onChange={(e) => setPreset(e.target.value)}
            >
              {Object.entries(SCAN_PRESETS).map(([key, p]) => (
                <option key={key} value={key}>{p.label}</option>
              ))}
            </select>
          </div>

          <div style={{ display: "flex", gap: "12px" }}>
            <button
              style={{ ...styles.button, flex: 1 }}
              onClick={startScan}
              disabled={loading}
            >
              START SCAN
            </button>
            <button
              style={{ ...styles.buttonSecondary }}
              onClick={() => loadAll(token)}
              disabled={loading}
            >
              REFRESH
            </button>
          </div>
        </div>
      </section>

      {/* Recent Scans */}
      <section style={styles.card}>
        <h2 style={{
          marginBottom: "20px",
          color: colors.primary,
          fontSize: "24px",
          fontWeight: 600,
        }}>
          Recent Scans
        </h2>

        {loading ? (
          <div style={{ color: colors.textSecondary, padding: "20px", textAlign: "center" }}>
            Loading scans...
          </div>
        ) : recentScans.length === 0 ? (
          <div style={{ color: colors.textMuted, padding: "20px", textAlign: "center" }}>
            No scans yet. Create an asset and run your first scan!
          </div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={styles.tableHeader}>Status</th>
                  <th style={styles.tableHeader}>Type</th>
                  <th style={styles.tableHeader}>Plugin</th>
                  <th style={styles.tableHeader}>Scan ID</th>
                </tr>
              </thead>
              <tbody>
                {recentScans.map((s) => (
                  <tr key={s.id}>
                    <td style={styles.tableCell}>
                      <span style={{
                        color: getStatusColor(s.status),
                        fontWeight: 600,
                        textTransform: "uppercase",
                        fontSize: "12px",
                      }}>
                        {s.status}
                      </span>
                    </td>
                    <td style={styles.tableCell}>{s.scan_type}</td>
                    <td style={styles.tableCell}>{s.plugin}</td>
                    <td style={{
                      ...styles.tableCell,
                      fontFamily: "monospace",
                      fontSize: "12px",
                      color: colors.textMuted,
                    }}>
                      {s.id.substring(0, 8)}...
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}

function StatCard({ title, value }: { title: string; value: any }) {
  return (
    <div style={styles.statCard}>
      <div style={styles.statTitle}>{title}</div>
      <div style={styles.statValue}>{value}</div>
      <div style={{
        position: "absolute",
        bottom: 0,
        left: 0,
        right: 0,
        height: "3px",
        background: `linear-gradient(90deg, transparent, ${colors.primary}, transparent)`,
      }} />
    </div>
  );
}
