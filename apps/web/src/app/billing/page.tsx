"use client";
import { useEffect, useState } from "react";
import Navigation from "@/components/Navigation";
import { apiFetch } from "@/lib/api";
import { colors, styles } from "@/styles/theme";

const PLANS = [
  { id: "starter", name: "Starter", price: 99, desc: "Basic vulnerability scanning" },
  { id: "professional", name: "Professional", price: 299, desc: "SOCaaS + scanning" },
  { id: "enterprise", name: "Enterprise", price: 599, desc: "Full PTaaS + SOCaaS + scanning" },
];

export default function BillingPage() {
  const [plan, setPlan] = useState("starter");
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState<string | null>(null);

  useEffect(() => {
    const t = localStorage.getItem("ts_token");
    if (!t) {
      window.location.href = "/login";
      return;
    }
    const params = new URLSearchParams(window.location.search);
    if (params.get("success")) setMsg("Subscription updated successfully");
    if (params.get("canceled")) setErr("Checkout canceled");
    const devUpgrade = params.get("dev_upgrade");

    apiFetch("/customers/me", {}, t)
      .then((c) => {
        setPlan(c.plan);
        if (devUpgrade) setMsg(`Plan set to ${devUpgrade} (dev mode)`);
      })
      .catch(() => (window.location.href = "/login"));
  }, []);

  async function upgrade(planId: string) {
    setLoading(planId);
    setErr("");
    setMsg("");
    try {
      const result = await apiFetch("/billing/checkout", {
        method: "POST",
        body: JSON.stringify({ plan: planId }),
      });
      if (result.url && !result.dev_mode) {
        window.location.href = result.url;
        return;
      }
      setPlan(planId);
      setMsg(`Plan upgraded to ${planId}${result.dev_mode ? " (local/dev — Stripe not configured)" : ""}`);
    } catch (e: any) {
      setErr(e.message || "Checkout failed");
    } finally {
      setLoading(null);
    }
  }

  return (
    <main style={{ padding: "24px", maxWidth: "960px", margin: "0 auto" }}>
      <Navigation />
      <h1 style={{ color: colors.textPrimary, marginBottom: 8 }}>Billing</h1>
      <p style={{ color: colors.textSecondary, marginBottom: 24, fontSize: 14 }}>
        Current plan: <span style={{ color: colors.primary, textTransform: "uppercase" }}>{plan}</span>
      </p>

      {msg && <div style={{ ...styles.alert, ...styles.alertSuccess, marginBottom: 16 }}>{msg}</div>}
      {err && <div style={{ ...styles.alert, ...styles.alertError, marginBottom: 16 }}>{err}</div>}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 16 }}>
        {PLANS.map((p) => (
          <div key={p.id} style={{
            ...styles.card,
            borderColor: plan === p.id ? colors.primary : undefined,
            boxShadow: plan === p.id ? `0 0 20px rgba(0,102,255,0.25)` : undefined,
          }}>
            <h3 style={{ color: colors.textPrimary, marginTop: 0 }}>{p.name}</h3>
            <p style={{ color: colors.primary, fontSize: 28, fontWeight: 700, margin: "8px 0" }}>
              ${p.price}<span style={{ fontSize: 14, color: colors.textSecondary }}>/mo</span>
            </p>
            <p style={{ color: colors.textSecondary, fontSize: 13, minHeight: 40 }}>{p.desc}</p>
            <button
              disabled={plan === p.id || loading === p.id}
              onClick={() => upgrade(p.id)}
              style={{
                ...styles.button,
                width: "100%",
                opacity: plan === p.id ? 0.6 : 1,
              }}
            >
              {plan === p.id ? "CURRENT" : loading === p.id ? "..." : "UPGRADE"}
            </button>
          </div>
        ))}
      </div>
    </main>
  );
}
