"use client";
import { useState } from "react";
import { apiFetch } from "@/lib/api";
import { colors, styles } from "@/styles/theme";

export default function RegisterPage() {
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  async function onRegister(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setErr("");
    setLoading(true);
    const form = e.currentTarget;
    const body = {
      full_name: (form.elements.namedItem("full_name") as HTMLInputElement).value,
      company_name: (form.elements.namedItem("company_name") as HTMLInputElement).value,
      email: (form.elements.namedItem("email") as HTMLInputElement).value,
      password: (form.elements.namedItem("password") as HTMLInputElement).value,
    };
    try {
      const data = await apiFetch("/auth/register", {
        method: "POST",
        body: JSON.stringify(body),
      });
      localStorage.setItem("ts_token", data.access_token);
      window.location.href = "/dashboard";
    } catch (e: any) {
      setErr(e.message || "Registration failed");
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
    }}>
      <div className="scanner-line" />
      <div style={{ ...styles.cardGlow, maxWidth: "480px", width: "100%", padding: "40px" }}>
        <h1 style={{
          fontSize: "32px",
          fontWeight: 700,
          color: colors.primary,
          textAlign: "center",
          marginBottom: "8px",
          letterSpacing: "2px",
        }}>
          CREATE ACCOUNT
        </h1>
        <p style={{
          textAlign: "center",
          color: colors.textSecondary,
          marginBottom: "28px",
          fontSize: "13px",
        }}>
          Start protecting your business with ThreatSense
        </p>

        {err && (
          <div style={{ ...styles.alert, ...styles.alertError, marginBottom: "16px" }}>{err}</div>
        )}

        <form onSubmit={onRegister} style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
          <input name="full_name" placeholder="Full name" required style={styles.input} />
          <input name="company_name" placeholder="Company name" required style={styles.input} />
          <input name="email" type="email" placeholder="Work email" required style={styles.input} />
          <input name="password" type="password" placeholder="Password (min 8 chars)" minLength={8} required style={styles.input} />
          <button type="submit" disabled={loading} style={styles.button}>
            {loading ? "CREATING..." : "REGISTER"}
          </button>
        </form>

        <p style={{ marginTop: "20px", textAlign: "center", color: colors.textSecondary, fontSize: "13px" }}>
          Already have an account?{" "}
          <a href="/login" style={{ color: colors.primary }}>Sign in</a>
        </p>
      </div>
    </main>
  );
}
