"use client";
import { useEffect, useState } from "react";
import Navigation from "@/components/Navigation";
import { colors, styles } from "@/styles/theme";
import { apiFetch } from "@/lib/api";

type Finding = {
  id: string;
  title: string;
  description: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  status: "open" | "in_progress" | "resolved" | "false_positive" | "accepted_risk";
  finding_type: string;
  cvss_score?: number;
  cve_id?: string;
  cwe_id?: string;
  affected_resource?: string;
  proof_of_concept?: string;
  remediation?: string;
  references?: string[];
  tags?: string[];
  asset_id: string;
  scan_id: string;
  created_at: string;
  updated_at: string;
  resolved_at?: string;
};

type FindingStats = {
  total: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  info: number;
  open: number;
  resolved: number;
  in_progress: number;
};

export default function FindingsPage() {
  const [token, setToken] = useState("");
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState("");

  const [findings, setFindings] = useState<Finding[]>([]);
  const [stats, setStats] = useState<FindingStats | null>(null);
  const [selectedFinding, setSelectedFinding] = useState<Finding | null>(null);

  // Filters
  const [severityFilter, setSeverityFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  async function loadData(t: string) {
    setErr("");
    setLoading(true);
    try {
      const [findingsData, statsData] = await Promise.all([
        apiFetch("/findings", {}, t),
        apiFetch("/findings/stats", {}, t)
      ]);

      setFindings(findingsData);
      setStats(statsData);
    } catch (e: any) {
      setErr(e?.message || "Failed to load findings.");
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
    loadData(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function updateFindingStatus(findingId: string, newStatus: string) {
    try {
      await apiFetch(
        `/findings/${findingId}`,
        {
          method: "PATCH",
          body: JSON.stringify({ status: newStatus })
        },
        token
      );
      await loadData(token);
      setSelectedFinding(null);
    } catch (e: any) {
      setErr(e?.message || "Failed to update finding.");
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "critical": return colors.critical;
      case "high": return colors.high;
      case "medium": return colors.medium;
      case "low": return colors.low;
      default: return colors.textMuted;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "resolved": return colors.success;
      case "in_progress": return colors.info;
      case "open": return colors.warning;
      case "false_positive": return colors.textMuted;
      default: return colors.textSecondary;
    }
  };

  const filteredFindings = findings.filter(f => {
    if (severityFilter !== "all" && f.severity !== severityFilter) return false;
    if (statusFilter !== "all" && f.status !== statusFilter) return false;
    return true;
  });

  return (
    <main style={{ ...styles.container, position: "relative", minHeight: "100vh" }}>
      <div className="scanner-line" />

      <Navigation />

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
        <div>
          <h1 style={{
            fontSize: "40px",
            margin: 0,
            marginBottom: "8px",
            color: colors.textPrimary,
            fontWeight: 700,
          }}>
            Security Findings
          </h1>
          <p style={{
            margin: 0,
            color: colors.textSecondary,
            fontSize: "16px",
          }}>
            Vulnerabilities discovered across your attack surface
          </p>
        </div>

        <button
          style={styles.button}
          onClick={() => loadData(token)}
          disabled={loading}
        >
          REFRESH
        </button>
      </div>

      {err && (
        <div style={{ ...styles.alert, ...styles.alertError }}>
          <strong>Error:</strong> {err}
        </div>
      )}

      {/* Stats Overview */}
      {stats && (
        <section style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
          gap: "16px",
          marginBottom: "32px",
        }}>
          <StatCard title="Total" value={stats.total} color={colors.primary} />
          <StatCard title="Critical" value={stats.critical} color={colors.critical} />
          <StatCard title="High" value={stats.high} color={colors.high} />
          <StatCard title="Medium" value={stats.medium} color={colors.medium} />
          <StatCard title="Low" value={stats.low} color={colors.low} />
          <StatCard title="Open" value={stats.open} color={colors.warning} />
          <StatCard title="In Progress" value={stats.in_progress} color={colors.info} />
          <StatCard title="Resolved" value={stats.resolved} color={colors.success} />
        </section>
      )}

      {/* Filters */}
      <section style={{ ...styles.card, marginBottom: "24px", padding: "16px" }}>
        <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
          <div style={{ flex: 1 }}>
            <label style={{ ...styles.label, marginBottom: "8px" }}>Severity</label>
            <select
              style={styles.select}
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
            >
              <option value="all">All Severities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
              <option value="info">Info</option>
            </select>
          </div>

          <div style={{ flex: 1 }}>
            <label style={{ ...styles.label, marginBottom: "8px" }}>Status</label>
            <select
              style={styles.select}
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="all">All Statuses</option>
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="false_positive">False Positive</option>
            </select>
          </div>

          <div style={{ flex: 1, display: "flex", gap: "8px", alignItems: "flex-end" }}>
            <button
              style={{ ...styles.buttonSecondary, flex: 1, padding: "10px" }}
              onClick={() => {
                setSeverityFilter("all");
                setStatusFilter("all");
              }}
            >
              CLEAR FILTERS
            </button>
          </div>
        </div>
      </section>

      {/* Findings List */}
      <section style={styles.card}>
        <h2 style={{
          marginBottom: "20px",
          color: colors.primary,
          fontSize: "24px",
          fontWeight: 600,
        }}>
          Findings ({filteredFindings.length})
        </h2>

        {loading ? (
          <div style={{ color: colors.textSecondary, padding: "40px", textAlign: "center" }}>
            Loading findings...
          </div>
        ) : filteredFindings.length === 0 ? (
          <div style={{ padding: "40px", textAlign: "center" }}>
            <div style={{ fontSize: "48px", marginBottom: "16px" }}>🎉</div>
            <p style={{ color: colors.textSecondary, fontSize: "16px" }}>
              {findings.length === 0
                ? "No findings yet. Run a scan to discover vulnerabilities."
                : "No findings match your current filters."}
            </p>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            {filteredFindings.map((finding) => (
              <div
                key={finding.id}
                style={{
                  ...styles.card,
                  padding: "16px",
                  cursor: "pointer",
                  border: `1px solid ${selectedFinding?.id === finding.id ? colors.borderPrimary : colors.borderSecondary}`,
                  transition: "all 0.2s",
                }}
                onClick={() => setSelectedFinding(finding)}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "8px" }}>
                      <span style={{
                        background: getSeverityColor(finding.severity),
                        color: "#000",
                        padding: "4px 12px",
                        borderRadius: "4px",
                        fontSize: "11px",
                        fontWeight: 700,
                        textTransform: "uppercase",
                      }}>
                        {finding.severity}
                      </span>

                      {finding.cvss_score && (
                        <span style={{
                          color: colors.textSecondary,
                          fontSize: "12px",
                          fontWeight: 600,
                        }}>
                          CVSS: {finding.cvss_score}
                        </span>
                      )}

                      {finding.cve_id && (
                        <span style={{
                          color: colors.accent,
                          fontSize: "12px",
                          fontWeight: 600,
                        }}>
                          {finding.cve_id}
                        </span>
                      )}

                      <span style={{
                        background: getStatusColor(finding.status) + "33",
                        color: getStatusColor(finding.status),
                        padding: "4px 12px",
                        borderRadius: "4px",
                        fontSize: "11px",
                        fontWeight: 600,
                        textTransform: "uppercase",
                      }}>
                        {finding.status.replace("_", " ")}
                      </span>
                    </div>

                    <h3 style={{
                      fontSize: "18px",
                      fontWeight: 600,
                      color: colors.textPrimary,
                      margin: "0 0 8px 0",
                    }}>
                      {finding.title}
                    </h3>

                    <p style={{
                      fontSize: "14px",
                      color: colors.textSecondary,
                      margin: 0,
                      lineHeight: "1.5",
                    }}>
                      {finding.description.length > 200
                        ? finding.description.substring(0, 200) + "..."
                        : finding.description}
                    </p>

                    {finding.affected_resource && (
                      <p style={{
                        fontSize: "12px",
                        color: colors.textMuted,
                        marginTop: "8px",
                        fontFamily: "monospace",
                      }}>
                        📍 {finding.affected_resource}
                      </p>
                    )}
                  </div>

                  <button
                    style={{
                      ...styles.buttonSecondary,
                      padding: "6px 12px",
                      fontSize: "12px",
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedFinding(finding);
                    }}
                  >
                    VIEW DETAILS
                  </button>
                </div>

                {finding.tags && finding.tags.length > 0 && (
                  <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginTop: "12px" }}>
                    {finding.tags.map((tag, idx) => (
                      <span
                        key={idx}
                        style={{
                          background: colors.bgSecondary,
                          color: colors.primary,
                          padding: "2px 8px",
                          borderRadius: "4px",
                          fontSize: "11px",
                          border: `1px solid ${colors.borderSecondary}`,
                        }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Finding Detail Modal */}
      {selectedFinding && (
        <div style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: "rgba(0, 0, 0, 0.85)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 1000,
          padding: "24px",
        }}
          onClick={() => setSelectedFinding(null)}
        >
          <div
            style={{
              ...styles.cardGlow,
              maxWidth: "900px",
              width: "100%",
              maxHeight: "90vh",
              overflow: "auto",
              padding: "32px",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "24px" }}>
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", gap: "12px", marginBottom: "12px", flexWrap: "wrap" }}>
                  <span style={{
                    background: getSeverityColor(selectedFinding.severity),
                    color: "#000",
                    padding: "6px 16px",
                    borderRadius: "6px",
                    fontSize: "13px",
                    fontWeight: 700,
                    textTransform: "uppercase",
                  }}>
                    {selectedFinding.severity}
                  </span>

                  {selectedFinding.cvss_score && (
                    <span style={{
                      background: colors.bgSecondary,
                      color: colors.textPrimary,
                      padding: "6px 16px",
                      borderRadius: "6px",
                      fontSize: "13px",
                      fontWeight: 600,
                    }}>
                      CVSS: {selectedFinding.cvss_score}
                    </span>
                  )}

                  {selectedFinding.cve_id && (
                    <span style={{
                      background: colors.bgSecondary,
                      color: colors.accent,
                      padding: "6px 16px",
                      borderRadius: "6px",
                      fontSize: "13px",
                      fontWeight: 600,
                    }}>
                      {selectedFinding.cve_id}
                    </span>
                  )}

                  {selectedFinding.cwe_id && (
                    <span style={{
                      background: colors.bgSecondary,
                      color: colors.textSecondary,
                      padding: "6px 16px",
                      borderRadius: "6px",
                      fontSize: "13px",
                      fontWeight: 600,
                    }}>
                      {selectedFinding.cwe_id}
                    </span>
                  )}
                </div>

                <h2 style={{
                  fontSize: "28px",
                  fontWeight: 700,
                  color: colors.textPrimary,
                  margin: "0 0 12px 0",
                }}>
                  {selectedFinding.title}
                </h2>
              </div>

              <button
                style={{
                  background: "transparent",
                  border: "none",
                  color: colors.textSecondary,
                  fontSize: "32px",
                  cursor: "pointer",
                  padding: "0 8px",
                }}
                onClick={() => setSelectedFinding(null)}
              >
                ×
              </button>
            </div>

            {/* Description */}
            <Section title="Description">
              <p style={{ color: colors.textSecondary, lineHeight: "1.6", margin: 0 }}>
                {selectedFinding.description}
              </p>
            </Section>

            {/* Affected Resource */}
            {selectedFinding.affected_resource && (
              <Section title="Affected Resource">
                <code style={{
                  display: "block",
                  background: colors.bgSecondary,
                  padding: "12px",
                  borderRadius: "6px",
                  color: colors.accent,
                  fontFamily: "monospace",
                  fontSize: "14px",
                }}>
                  {selectedFinding.affected_resource}
                </code>
              </Section>
            )}

            {/* Proof of Concept */}
            {selectedFinding.proof_of_concept && (
              <Section title="Proof of Concept">
                <code style={{
                  display: "block",
                  background: colors.bgSecondary,
                  padding: "12px",
                  borderRadius: "6px",
                  color: colors.warning,
                  fontFamily: "monospace",
                  fontSize: "13px",
                  whiteSpace: "pre-wrap",
                }}>
                  {selectedFinding.proof_of_concept}
                </code>
              </Section>
            )}

            {/* Remediation */}
            {selectedFinding.remediation && (
              <Section title="Remediation">
                <p style={{ color: colors.success, lineHeight: "1.6", margin: 0 }}>
                  {selectedFinding.remediation}
                </p>
              </Section>
            )}

            {/* References */}
            {selectedFinding.references && selectedFinding.references.length > 0 && (
              <Section title="References">
                <ul style={{ margin: 0, paddingLeft: "20px" }}>
                  {selectedFinding.references.map((ref, idx) => (
                    <li key={idx} style={{ marginBottom: "8px" }}>
                      <a
                        href={ref}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          color: colors.primary,
                          textDecoration: "none",
                          fontSize: "14px",
                        }}
                      >
                        {ref}
                      </a>
                    </li>
                  ))}
                </ul>
              </Section>
            )}

            {/* Tags */}
            {selectedFinding.tags && selectedFinding.tags.length > 0 && (
              <Section title="Tags">
                <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                  {selectedFinding.tags.map((tag, idx) => (
                    <span
                      key={idx}
                      style={{
                        background: colors.bgSecondary,
                        color: colors.primary,
                        padding: "6px 12px",
                        borderRadius: "4px",
                        fontSize: "12px",
                        border: `1px solid ${colors.borderSecondary}`,
                      }}
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </Section>
            )}

            {/* Actions */}
            <div style={{
              display: "flex",
              gap: "12px",
              marginTop: "32px",
              paddingTop: "24px",
              borderTop: `1px solid ${colors.borderSecondary}`,
            }}>
              {selectedFinding.status === "open" && (
                <>
                  <button
                    style={{ ...styles.button, flex: 1 }}
                    onClick={() => updateFindingStatus(selectedFinding.id, "in_progress")}
                  >
                    MARK IN PROGRESS
                  </button>
                  <button
                    style={{ ...styles.buttonSecondary, flex: 1 }}
                    onClick={() => updateFindingStatus(selectedFinding.id, "false_positive")}
                  >
                    FALSE POSITIVE
                  </button>
                </>
              )}

              {selectedFinding.status === "in_progress" && (
                <button
                  style={{ ...styles.button, flex: 1, background: colors.success }}
                  onClick={() => updateFindingStatus(selectedFinding.id, "resolved")}
                >
                  MARK RESOLVED
                </button>
              )}

              {selectedFinding.status === "resolved" && (
                <button
                  style={{ ...styles.button, flex: 1 }}
                  onClick={() => updateFindingStatus(selectedFinding.id, "open")}
                >
                  REOPEN
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

function StatCard({ title, value, color }: { title: string; value: number; color: string }) {
  return (
    <div style={{
      ...styles.card,
      padding: "16px",
      textAlign: "center",
    }}>
      <div style={{
        fontSize: "12px",
        fontWeight: 600,
        color: colors.textSecondary,
        textTransform: "uppercase",
        letterSpacing: "0.5px",
        marginBottom: "8px",
      }}>
        {title}
      </div>
      <div style={{
        fontSize: "32px",
        fontWeight: 700,
        color: color,
        textShadow: `0 0 10px ${color}88`,
      }}>
        {value}
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: "24px" }}>
      <h3 style={{
        fontSize: "16px",
        fontWeight: 600,
        color: colors.primary,
        textTransform: "uppercase",
        letterSpacing: "0.5px",
        marginBottom: "12px",
      }}>
        {title}
      </h3>
      {children}
    </div>
  );
}
