import { useEffect, useState } from "react";
import { ScrollView, StyleSheet, Text, View } from "react-native";
import { apiFetch } from "../api";
import NavBar from "../components/NavBar";
import { colors } from "../theme";

export default function DashboardScreen({ nav }: { nav: any }) {
  const [assets, setAssets] = useState(0);
  const [scans, setScans] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    Promise.all([
      apiFetch("/assets"),
      apiFetch("/scans"),
      apiFetch("/findings/stats"),
    ])
      .then(([a, s, st]) => {
        setAssets(a.length);
        setScans(s.slice(0, 8));
        setStats(st);
      })
      .catch(() => nav.logout());
  }, []);

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ padding: 16 }}>
      <NavBar current="dashboard" onNavigate={nav.go} onLogout={nav.logout} />
      <Text style={styles.h1}>Dashboard</Text>
      <View style={styles.row}>
        <Card label="Assets" value={String(assets)} />
        <Card label="Findings" value={String(stats?.total ?? 0)} />
        <Card label="Critical" value={String(stats?.critical ?? 0)} />
      </View>
      <Text style={styles.h2}>Recent scans</Text>
      {scans.map((s) => (
        <View key={s.id} style={styles.item}>
          <Text style={styles.itemTitle}>{s.plugin}</Text>
          <Text style={styles.itemMeta}>
            {s.status} · {s.id.slice(0, 8)}
          </Text>
        </View>
      ))}
      {!scans.length && <Text style={styles.muted}>No scans yet</Text>}
    </ScrollView>
  );
}

function Card({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.card}>
      <Text style={styles.cardValue}>{value}</Text>
      <Text style={styles.cardLabel}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  h1: { color: colors.text, fontSize: 28, fontWeight: "700", marginBottom: 16 },
  h2: { color: colors.text, fontSize: 18, fontWeight: "600", marginVertical: 12 },
  row: { flexDirection: "row", gap: 10, marginBottom: 8 },
  card: {
    flex: 1,
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 10,
    padding: 12,
  },
  cardValue: { color: colors.primary, fontSize: 22, fontWeight: "700" },
  cardLabel: { color: colors.muted, fontSize: 12, marginTop: 4 },
  item: {
    backgroundColor: colors.card,
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: colors.border,
  },
  itemTitle: { color: colors.text, fontWeight: "600" },
  itemMeta: { color: colors.muted, fontSize: 12, marginTop: 4 },
  muted: { color: colors.muted },
});
