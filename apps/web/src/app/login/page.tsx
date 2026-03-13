"use client";
import { useState } from "react";
import { apiFetch } from "@/lib/api";
import { colors, styles } from "@/styles/theme";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  async function onLogin(e?: React.FormEvent<HTMLFormElement>) {
    if (e) e.preventDefault();
    setErr("");
    setLoading(true);

    // Read directly from DOM to handle browser autofill (which skips React onChange)
    const form = e?.currentTarget;
    const emailVal = (form?.elements.namedItem("email") as HTMLInputElement)?.value ?? email;
    const passwordVal = (form?.elements.namedItem("password") as HTMLInputElement)?.value ?? password;

    try {
      const data = await apiFetch("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email: emailVal, password: passwordVal })
      });
      localStorage.setItem("ts_token", data.access_token);
      window.location.href = "/dashboard";
    } catch (e: any) {
      setErr(e.message || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

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
        ...styles.cardGlow,
        maxWidth: "440px",
        width: "100%",
        padding: "40px",
      }}>
        {/* Logo/Header */}
        <div style={{ textAlign: "center", marginBottom: "32px" }}>
          <h1 style={{
            fontSize: "36px",
            fontWeight: 700,
            color: colors.primary,
            marginBottom: "8px",
            textShadow: `0 0 20px rgba(0, 102, 255, 0.6)`,
            letterSpacing: "2px",
          }}>
            THREATSENSE
          </h1>
          <p style={{
            fontSize: "14px",
            color: colors.textSecondary,
            textTransform: "uppercase",
            letterSpacing: "3px",
          }}>
            Security Platform
          </p>
        </div>

        {/* Demo Credentials Notice */}
        <div style={{
          ...styles.alert,
          ...styles.alertInfo,
          marginBottom: "24px",
          fontSize: "12px",
          textAlign: "center",
        }}>
          <strong>Demo Login:</strong> demo@threatsense.com / demo123
        </div>

        {/* Error Message */}
        {err && (
          <div style={{
            ...styles.alert,
            ...styles.alertError,
          }}>
            <strong>Error:</strong> {err}
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={onLogin}>
          <div style={{ marginBottom: "20px" }}>
            <label style={styles.label}>Email Address</label>
            <input
              type="email"
              name="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              style={styles.input}
              required
              disabled={loading}
            />
          </div>

          <div style={{ marginBottom: "24px" }}>
            <label style={styles.label}>Password</label>
            <input
              type="password"
              name="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              style={styles.input}
              required
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            style={{
              ...styles.button,
              width: "100%",
              fontSize: "16px",
              padding: "14px",
              opacity: loading ? 0.6 : 1,
              cursor: loading ? "not-allowed" : "pointer",
            }}
            disabled={loading}
          >
            {loading ? "AUTHENTICATING..." : "LOGIN"}
          </button>
        </form>

        {/* Footer */}
        <div style={{
          marginTop: "32px",
          paddingTop: "24px",
          borderTop: `1px solid ${colors.borderSecondary}`,
          textAlign: "center",
        }}>
          <p style={{
            fontSize: "12px",
            color: colors.textMuted,
          }}>
            Automated SOCaaS • PTaaS • Vulnerability Scanning
          </p>
        </div>
      </div>
    </main>
  );
}
