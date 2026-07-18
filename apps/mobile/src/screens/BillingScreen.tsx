import { useEffect, useState } from "react";
import {
  Linking,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { apiFetch } from "../api";
import NavBar from "../components/NavBar";
import { colors } from "../theme";

const PLANS = [
  { id: "starter", name: "Starter", price: 99 },
  { id: "professional", name: "Professional", price: 299 },
  { id: "enterprise", name: "Enterprise", price: 599 },
];

export default function BillingScreen({ nav }: { nav: any }) {
  const [plan, setPlan] = useState("starter");
  const [msg, setMsg] = useState("");

  useEffect(() => {
    apiFetch("/customers/me")
      .then((c) => setPlan(c.plan))
      .catch(() => nav.logout());
  }, []);

  async function upgrade(planId: string) {
    setMsg("");
    try {
      const result = await apiFetch("/billing/checkout", {
        method: "POST",
        body: JSON.stringify({ plan: planId }),
      });
      if (result.url && !result.dev_mode) {
        await Linking.openURL(result.url);
        return;
      }
      setPlan(planId);
      setMsg(`Upgraded to ${planId}${result.dev_mode ? " (dev mode)" : ""}`);
    } catch (e: any) {
      setMsg(e.message);
    }
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ padding: 16 }}>
      <NavBar current="billing" onNavigate={nav.go} onLogout={nav.logout} />
      <Text style={styles.h1}>Billing</Text>
      <Text style={styles.current}>Current: {plan.toUpperCase()}</Text>
      {PLANS.map((p) => (
        <View key={p.id} style={styles.card}>
          <Text style={styles.name}>{p.name}</Text>
          <Text style={styles.price}>${p.price}/mo</Text>
          <Pressable
            style={[styles.btn, plan === p.id && styles.btnDisabled]}
            disabled={plan === p.id}
            onPress={() => upgrade(p.id)}
          >
            <Text style={styles.btnText}>{plan === p.id ? "CURRENT" : "UPGRADE"}</Text>
          </Pressable>
        </View>
      ))}
      {!!msg && <Text style={styles.msg}>{msg}</Text>}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  h1: { color: colors.text, fontSize: 28, fontWeight: "700", marginBottom: 8 },
  current: { color: colors.primary, marginBottom: 16, fontWeight: "600" },
  card: {
    backgroundColor: colors.card,
    borderRadius: 10,
    padding: 14,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: colors.border,
  },
  name: { color: colors.text, fontSize: 18, fontWeight: "700" },
  price: { color: colors.primary, fontSize: 22, fontWeight: "700", marginVertical: 8 },
  btn: { backgroundColor: colors.primary, padding: 10, borderRadius: 6, alignItems: "center" },
  btnDisabled: { opacity: 0.5 },
  btnText: { color: colors.text, fontWeight: "700", fontSize: 12 },
  msg: { color: colors.success, marginTop: 12 },
});
