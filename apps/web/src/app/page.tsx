"use client";
import { colors, styles } from "@/styles/theme";

export default function HomePage() {
  return (
    <main style={{
      minHeight: "100vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "24px",
      position: "relative",
    }}>
      <div className="scanner-line" />

      <div style={{
        textAlign: "center",
        maxWidth: "900px",
      }}>
        {/* Hero Section */}
        <h1 style={{
          fontSize: "64px",
          fontWeight: 700,
          color: colors.primary,
          marginBottom: "16px",
          textShadow: `0 0 30px rgba(0, 102, 255, 0.8)`,
          letterSpacing: "4px",
        }}>
          THREATSENSE
        </h1>

        <p style={{
          fontSize: "20px",
          color: colors.textSecondary,
          marginBottom: "12px",
          textTransform: "uppercase",
          letterSpacing: "4px",
        }}>
          Automated Security Platform
        </p>

        <p style={{
          fontSize: "16px",
          color: colors.textMuted,
          marginBottom: "48px",
          lineHeight: "1.6",
        }}>
          Lightweight SOCaaS • PTaaS • Vulnerability Scanning<br />
          Built for Small Businesses
        </p>

        {/* Feature Cards */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
          gap: "20px",
          marginBottom: "48px",
        }}>
          <div style={styles.cardGlow}>
            <h3 style={{
              color: colors.primary,
              fontSize: "18px",
              marginBottom: "12px",
              fontWeight: 600,
            }}>SOCaaS</h3>
            <p style={{
              color: colors.textSecondary,
              fontSize: "14px",
              lineHeight: "1.6",
            }}>
              Security Operations Center as a Service with automated threat detection
            </p>
          </div>

          <div style={styles.cardGlow}>
            <h3 style={{
              color: colors.primary,
              fontSize: "18px",
              marginBottom: "12px",
              fontWeight: 600,
            }}>PTaaS</h3>
            <p style={{
              color: colors.textSecondary,
              fontSize: "14px",
              lineHeight: "1.6",
            }}>
              Penetration Testing as a Service to identify vulnerabilities
            </p>
          </div>

          <div style={styles.cardGlow}>
            <h3 style={{
              color: colors.primary,
              fontSize: "18px",
              marginBottom: "12px",
              fontWeight: 600,
            }}>Vuln Scanning</h3>
            <p style={{
              color: colors.textSecondary,
              fontSize: "14px",
              lineHeight: "1.6",
            }}>
              Continuous vulnerability scanning and compliance monitoring
            </p>
          </div>
        </div>

        {/* CTA Buttons */}
        <div style={{
          display: "flex",
          gap: "16px",
          justifyContent: "center",
          flexWrap: "wrap",
        }}>
          <a href="/login" style={{ textDecoration: "none" }}>
            <button style={{
              ...styles.button,
              fontSize: "16px",
              padding: "14px 32px",
            }}>
              GET STARTED
            </button>
          </a>

          <a href="/dashboard" style={{ textDecoration: "none" }}>
            <button style={{
              ...styles.buttonSecondary,
              fontSize: "16px",
              padding: "14px 32px",
            }}>
              VIEW DASHBOARD
            </button>
          </a>
        </div>
      </div>
    </main>
  );
}
