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

export default function SettingsScreen({ nav }: { nav: any }) {
  const [notifyEmail, setNotifyEmail] = useState("");
  const [slack, setSlack] = useState("");
  const [discord, setDiscord] = useState("");
  const [msg, setMsg] = useState("");

  useEffect(() => {
    apiFetch("/customers/me")
      .then((c) => {
        setNotifyEmail(c.notify_email || "");
        setSlack(c.slack_webhook_url || "");
        setDiscord(c.discord_webhook_url || "");
      })
      .catch(() => nav.logout());
  }, []);

  async function save() {
    setMsg("");
    try {
      await apiFetch("/customers/me", {
        method: "PATCH",
        body: JSON.stringify({
          notify_email: notifyEmail,
          slack_webhook_url: slack,
          discord_webhook_url: discord,
        }),
      });
      setMsg("Saved");
    } catch (e: any) {
      setMsg(e.message);
    }
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ padding: 16 }}>
      <NavBar current="settings" onNavigate={nav.go} onLogout={nav.logout} />
      <Text style={styles.h1}>Settings</Text>
      <Text style={styles.label}>Notification email</Text>
      <TextInput style={styles.input} value={notifyEmail} onChangeText={setNotifyEmail} autoCapitalize="none" placeholderTextColor={colors.muted} />
      <Text style={styles.label}>Slack webhook</Text>
      <TextInput style={styles.input} value={slack} onChangeText={setSlack} autoCapitalize="none" placeholderTextColor={colors.muted} />
      <Text style={styles.label}>Discord webhook</Text>
      <TextInput style={styles.input} value={discord} onChangeText={setDiscord} autoCapitalize="none" placeholderTextColor={colors.muted} />
      <Pressable style={styles.btn} onPress={save}>
        <Text style={styles.btnText}>SAVE</Text>
      </Pressable>
      {!!msg && <Text style={styles.msg}>{msg}</Text>}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  h1: { color: colors.text, fontSize: 28, fontWeight: "700", marginBottom: 16 },
  label: { color: colors.muted, fontSize: 12, marginBottom: 6 },
  input: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 8,
    color: colors.text,
    padding: 12,
    marginBottom: 12,
  },
  btn: { backgroundColor: colors.primary, padding: 12, borderRadius: 8, alignItems: "center" },
  btnText: { color: colors.text, fontWeight: "700" },
  msg: { color: colors.success, marginTop: 12 },
});
