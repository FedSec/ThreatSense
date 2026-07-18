"use client";
import { useEffect, useState } from "react";
import Navigation from "@/components/Navigation";
import { apiFetch } from "@/lib/api";
import { colors, styles } from "@/styles/theme";

type Customer = {
  company_name: string;
  email: string;
  plan: string;
  notify_email?: string;
  slack_webhook_url?: string;
  discord_webhook_url?: string;
};

export default function SettingsPage() {
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const t = localStorage.getItem("ts_token");
    if (!t) {
      window.location.href = "/login";
      return;
    }
    apiFetch("/customers/me", {}, t)
      .then(setCustomer)
      .catch(() => (window.location.href = "/login"));
  }, []);

  async function onSave(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!customer) return;
    setSaving(true);
    setMsg("");
    setErr("");
    const form = e.currentTarget;
    const body = {
      company_name: (form.elements.namedItem("company_name") as HTMLInputElement).value,
      notify_email: (form.elements.namedItem("notify_email") as HTMLInputElement).value,
      slack_webhook_url: (form.elements.namedItem("slack_webhook_url") as HTMLInputElement).value,
      discord_webhook_url: (form.elements.namedItem("discord_webhook_url") as HTMLInputElement).value,
    };
    try {
      const updated = await apiFetch("/customers/me", {
        method: "PATCH",
        body: JSON.stringify(body),
      });
      setCustomer(updated);
      setMsg("Settings saved");
    } catch (e: any) {
      setErr(e.message || "Save failed");
    } finally {
      setSaving(false);
    }
  }

  if (!customer) {
    return (
      <main style={{ padding: "24px" }}>
        <Navigation />
        <p style={{ color: colors.textSecondary }}>Loading...</p>
      </main>
    );
  }

  return (
    <main style={{ padding: "24px", maxWidth: "800px", margin: "0 auto" }}>
      <Navigation />
      <h1 style={{ color: colors.textPrimary, marginBottom: "8px" }}>Settings</h1>
      <p style={{ color: colors.textSecondary, marginBottom: "24px", fontSize: "14px" }}>
        Notifications and integrations for {customer.email}
      </p>

      {msg && <div style={{ ...styles.alert, ...styles.alertSuccess, marginBottom: 16 }}>{msg}</div>}
      {err && <div style={{ ...styles.alert, ...styles.alertError, marginBottom: 16 }}>{err}</div>}

      <form onSubmit={onSave} style={{ ...styles.card, display: "flex", flexDirection: "column", gap: 14 }}>
        <label style={{ color: colors.textSecondary, fontSize: 12 }}>Company name</label>
        <input name="company_name" defaultValue={customer.company_name} style={styles.input} />

        <label style={{ color: colors.textSecondary, fontSize: 12 }}>Notification email</label>
        <input name="notify_email" type="email" defaultValue={customer.notify_email || ""} style={styles.input} />

        <label style={{ color: colors.textSecondary, fontSize: 12 }}>Slack webhook URL</label>
        <input name="slack_webhook_url" defaultValue={customer.slack_webhook_url || ""} style={styles.input} placeholder="https://hooks.slack.com/..." />

        <label style={{ color: colors.textSecondary, fontSize: 12 }}>Discord webhook URL</label>
        <input name="discord_webhook_url" defaultValue={customer.discord_webhook_url || ""} style={styles.input} placeholder="https://discord.com/api/webhooks/..." />

        <button type="submit" disabled={saving} style={styles.button}>
          {saving ? "SAVING..." : "SAVE SETTINGS"}
        </button>
      </form>
    </main>
  );
}
