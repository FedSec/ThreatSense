import { useEffect, useState } from "react";
import {
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { apiFetch } from "../api";
import NavBar from "../components/NavBar";
import { colors } from "../theme";

export default function FindingsScreen({ nav }: { nav: any }) {
  const [findings, setFindings] = useState<any[]>([]);
  const [selected, setSelected] = useState<any | null>(null);

  async function load() {
    try {
      setFindings(await apiFetch("/findings"));
    } catch {
      nav.logout();
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function setStatus(id: string, status: string) {
    await apiFetch(`/findings/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
    setSelected(null);
    await load();
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ padding: 16 }}>
      <NavBar current="findings" onNavigate={nav.go} onLogout={nav.logout} />
      <Text style={styles.h1}>Findings</Text>
      {findings.map((f) => (
        <Pressable key={f.id} style={styles.item} onPress={() => setSelected(f)}>
          <Text style={[styles.sev, { color: sevColor(f.severity) }]}>
            {f.severity.toUpperCase()}
          </Text>
          <Text style={styles.itemTitle}>{f.title}</Text>
          <Text style={styles.itemMeta}>{f.status}</Text>
        </Pressable>
      ))}
      {!findings.length && <Text style={styles.muted}>No findings yet</Text>}

      {selected && (
        <View style={styles.detail}>
          <Text style={styles.h2}>{selected.title}</Text>
          <Text style={styles.muted}>{selected.description}</Text>
          {!!selected.remediation && (
            <Text style={styles.body}>Fix: {selected.remediation}</Text>
          )}
          <View style={styles.actions}>
            <Pressable style={styles.btn} onPress={() => setStatus(selected.id, "in_progress")}>
              <Text style={styles.btnText}>IN PROGRESS</Text>
            </Pressable>
            <Pressable style={styles.btn} onPress={() => setStatus(selected.id, "resolved")}>
              <Text style={styles.btnText}>RESOLVE</Text>
            </Pressable>
            <Pressable style={styles.btnSecondary} onPress={() => setSelected(null)}>
              <Text style={styles.btnText}>CLOSE</Text>
            </Pressable>
          </View>
        </View>
      )}
    </ScrollView>
  );
}

function sevColor(s: string) {
  if (s === "critical") return colors.danger;
  if (s === "high") return "#ff6600";
  if (s === "medium") return colors.warning;
  return colors.muted;
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  h1: { color: colors.text, fontSize: 28, fontWeight: "700", marginBottom: 16 },
  h2: { color: colors.text, fontSize: 18, fontWeight: "700", marginBottom: 8 },
  item: {
    backgroundColor: colors.card,
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: colors.border,
  },
  sev: { fontSize: 11, fontWeight: "700", marginBottom: 4 },
  itemTitle: { color: colors.text, fontWeight: "600" },
  itemMeta: { color: colors.muted, fontSize: 12, marginTop: 4 },
  muted: { color: colors.muted },
  body: { color: colors.text, marginTop: 8 },
  detail: {
    marginTop: 16,
    padding: 14,
    borderRadius: 10,
    backgroundColor: colors.card,
    borderWidth: 1,
    borderColor: colors.primary,
  },
  actions: { flexDirection: "row", flexWrap: "wrap", gap: 8, marginTop: 12 },
  btn: { backgroundColor: colors.primary, padding: 10, borderRadius: 6 },
  btnSecondary: { backgroundColor: colors.border, padding: 10, borderRadius: 6 },
  btnText: { color: colors.text, fontWeight: "700", fontSize: 11 },
});
