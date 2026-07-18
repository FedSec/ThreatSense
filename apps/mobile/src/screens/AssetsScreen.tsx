import { useEffect, useState } from "react";
import {
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { apiFetch } from "../api";
import NavBar from "../components/NavBar";
import { colors } from "../theme";

export default function AssetsScreen({ nav }: { nav: any }) {
  const [assets, setAssets] = useState<any[]>([]);
  const [kind, setKind] = useState("domain");
  const [value, setValue] = useState("");
  const [err, setErr] = useState("");

  async function load() {
    try {
      setAssets(await apiFetch("/assets"));
    } catch {
      nav.logout();
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function add() {
    setErr("");
    try {
      await apiFetch("/assets", {
        method: "POST",
        body: JSON.stringify({ kind, value }),
      });
      setValue("");
      await load();
    } catch (e: any) {
      setErr(e.message);
    }
  }

  async function scan(assetId: string) {
    try {
      await apiFetch("/scans", {
        method: "POST",
        body: JSON.stringify({
          asset_id: assetId,
          scan_type: "vuln_scan",
          plugin: "nuclei_scan",
          parameters: { severities: ["medium", "high", "critical"] },
        }),
      });
      nav.go("dashboard");
    } catch (e: any) {
      setErr(e.message);
    }
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ padding: 16 }}>
      <NavBar current="assets" onNavigate={nav.go} onLogout={nav.logout} />
      <Text style={styles.h1}>Assets</Text>
      {!!err && <Text style={styles.err}>{err}</Text>}
      <TextInput
        style={styles.input}
        placeholder="Kind (domain, url, ip)"
        placeholderTextColor={colors.muted}
        value={kind}
        onChangeText={setKind}
      />
      <TextInput
        style={styles.input}
        placeholder="Value (example.com)"
        placeholderTextColor={colors.muted}
        value={value}
        onChangeText={setValue}
        autoCapitalize="none"
      />
      <Pressable style={styles.btn} onPress={add}>
        <Text style={styles.btnText}>ADD ASSET</Text>
      </Pressable>
      {assets.map((a) => (
        <View key={a.id} style={styles.item}>
          <Text style={styles.itemTitle}>{a.value}</Text>
          <Text style={styles.itemMeta}>{a.kind}</Text>
          <Pressable style={styles.scanBtn} onPress={() => scan(a.id)}>
            <Text style={styles.btnText}>SCAN</Text>
          </Pressable>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  h1: { color: colors.text, fontSize: 28, fontWeight: "700", marginBottom: 16 },
  input: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 8,
    color: colors.text,
    padding: 12,
    marginBottom: 10,
  },
  btn: {
    backgroundColor: colors.primary,
    padding: 12,
    borderRadius: 8,
    alignItems: "center",
    marginBottom: 16,
  },
  scanBtn: {
    backgroundColor: colors.primary,
    padding: 8,
    borderRadius: 6,
    alignItems: "center",
    marginTop: 8,
  },
  btnText: { color: colors.text, fontWeight: "700", fontSize: 12 },
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
  err: { color: colors.danger, marginBottom: 8 },
});
