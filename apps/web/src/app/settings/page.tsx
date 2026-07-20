"use client";
import { useEffect, useState } from "react";
import Navigation from "@/components/Navigation";
import { apiFetch } from "@/lib/api";
import { colors, styles } from "@/styles/theme";

type NotifyChannel = "email" | "telegram";

type Customer = {
  company_name: string;
  email: string;
  plan: string;
  notify_email?: string;
  notify_channel?: NotifyChannel;
  telegram_bot_token?: string;
  telegram_chat_id?: string;
  telegram_api_url?: string;
  slack_webhook_url?: string;
  discord_webhook_url?: string;
};

export default function SettingsPage() {
  const [customer, setCustomer] = useState<Customer | null>(null);
  const [channel, setChannel] = useState<NotifyChannel>("email");
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
      .then((c: Customer) => {
        setCustomer(c);
        setChannel(c.notify_channel === "telegram" ? "telegram" : "email");
      })
      .catch(() => (window.location.href = "/login"));
  }, []);

  async function onSave(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!customer) return;
    setSaving(true);
    setMsg("");
    setErr("");
    const form = e.currentTarget;
    const body: Record<string, string> = {
      company_name: (form.elements.namedItem("company_name") as HTMLInputElement).value,
      notify_channel: channel,
      slack_webhook_url: (form.elements.namedItem("slack_webhook_url") as HTMLInputElement).value,
      discord_webhook_url: (form.elements.namedItem("discord_webhook_url") as HTMLInputElement).value,
    };
    if (channel === "email") {
      body.notify_email = (form.elements.namedItem("notify_email") as HTMLInputElement).value;
    } else {
      body.telegram_bot_token = (form.elements.namedItem("telegram_bot_token") as HTMLInputElement).value;
      body.telegram_chat_id = (form.elements.namedItem("telegram_chat_id") as HTMLInputElement).value;
      body.telegram_api_url = (form.elements.namedItem("telegram_api_url") as HTMLInputElement).value;
    }
    try {
      const updated = await apiFetch("/customers/me", {
        method: "PATCH",
        body: JSON.stringify(body),
      });
      setCustomer(updated);
      setChannel(updated.notify_channel === "telegram" ? "telegram" : "email");
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

        <label style={{ color: colors.textSecondary, fontSize: 12 }}>Scan notification channel</label>
        <div style={{ display: "flex", gap: 16, marginBottom: 4 }}>
          <label style={{ color: colors.textPrimary, fontSize: 14, display: "flex", alignItems: "center", gap: 6 }}>
            <input
              type="radio"
              name="notify_channel"
              checked={channel === "email"}
              onChange={() => setChannel("email")}
            />
            Email (SMTP)
          </label>
          <label style={{ color: colors.textPrimary, fontSize: 14, display: "flex", alignItems: "center", gap: 6 }}>
            <input
              type="radio"
              name="notify_channel"
              checked={channel === "telegram"}
              onChange={() => setChannel("telegram")}
            />
            Telegram
          </label>
        </div>

        {channel === "email" ? (
          <>
            <label style={{ color: colors.textSecondary, fontSize: 12 }}>Notification email</label>
            <input
              name="notify_email"
              type="email"
              defaultValue={customer.notify_email || ""}
              style={styles.input}
            />
          </>
        ) : (
          <>
            <label style={{ color: colors.textSecondary, fontSize: 12 }}>Telegram bot token</label>
            <input
              name="telegram_bot_token"
              defaultValue={customer.telegram_bot_token || ""}
              style={styles.input}
              placeholder="123456:ABC-DEF..."
              autoComplete="off"
            />

            <label style={{ color: colors.textSecondary, fontSize: 12 }}>Telegram chat ID</label>
            <input
              name="telegram_chat_id"
              defaultValue={customer.telegram_chat_id || ""}
              style={styles.input}
              placeholder="-1001234567890"
            />

            <label style={{ color: colors.textSecondary, fontSize: 12 }}>Telegram API URL</label>
            <input
              name="telegram_api_url"
              defaultValue={customer.telegram_api_url || "https://api.telegram.org"}
              style={styles.input}
              placeholder="https://api.telegram.org"
            />
            <p style={{ color: colors.textSecondary, fontSize: 12, margin: "-6px 0 0" }}>
              Default is api.telegram.org. Use a custom Bot API host if needed.
            </p>
          </>
        )}

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
