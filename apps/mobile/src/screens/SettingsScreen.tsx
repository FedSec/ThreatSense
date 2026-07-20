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

type NotifyChannel = "email" | "telegram";

export default function SettingsScreen({ nav }: { nav: any }) {
  const [channel, setChannel] = useState<NotifyChannel>("email");
  const [notifyEmail, setNotifyEmail] = useState("");
  const [botToken, setBotToken] = useState("");
  const [chatId, setChatId] = useState("");
  const [apiUrl, setApiUrl] = useState("https://api.telegram.org");
  const [slack, setSlack] = useState("");
  const [discord, setDiscord] = useState("");
  const [msg, setMsg] = useState("");

  useEffect(() => {
    apiFetch("/customers/me")
      .then((c) => {
        setChannel(c.notify_channel === "telegram" ? "telegram" : "email");
        setNotifyEmail(c.notify_email || "");
        setBotToken(c.telegram_bot_token || "");
        setChatId(c.telegram_chat_id || "");
        setApiUrl(c.telegram_api_url || "https://api.telegram.org");
        setSlack(c.slack_webhook_url || "");
        setDiscord(c.discord_webhook_url || "");
      })
      .catch(() => nav.logout());
  }, []);

  async function save() {
    setMsg("");
    try {
      const body: Record<string, string> = {
        notify_channel: channel,
        slack_webhook_url: slack,
        discord_webhook_url: discord,
      };
      if (channel === "email") {
        body.notify_email = notifyEmail;
      } else {
        body.telegram_bot_token = botToken;
        body.telegram_chat_id = chatId;
        body.telegram_api_url = apiUrl;
      }
      await apiFetch("/customers/me", {
        method: "PATCH",
        body: JSON.stringify(body),
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

      <Text style={styles.label}>Scan notification channel</Text>
      <View style={styles.row}>
        <Pressable
          style={[styles.chip, channel === "email" && styles.chipActive]}
          onPress={() => setChannel("email")}
        >
          <Text style={styles.chipText}>Email (SMTP)</Text>
        </Pressable>
        <Pressable
          style={[styles.chip, channel === "telegram" && styles.chipActive]}
          onPress={() => setChannel("telegram")}
        >
          <Text style={styles.chipText}>Telegram</Text>
        </Pressable>
      </View>

      {channel === "email" ? (
        <>
          <Text style={styles.label}>Notification email</Text>
          <TextInput
            style={styles.input}
            value={notifyEmail}
            onChangeText={setNotifyEmail}
            autoCapitalize="none"
            placeholderTextColor={colors.muted}
          />
        </>
      ) : (
        <>
          <Text style={styles.label}>Telegram bot token</Text>
          <TextInput
            style={styles.input}
            value={botToken}
            onChangeText={setBotToken}
            autoCapitalize="none"
            placeholder="123456:ABC-DEF..."
            placeholderTextColor={colors.muted}
          />
          <Text style={styles.label}>Telegram chat ID</Text>
          <TextInput
            style={styles.input}
            value={chatId}
            onChangeText={setChatId}
            autoCapitalize="none"
            placeholder="-1001234567890"
            placeholderTextColor={colors.muted}
          />
          <Text style={styles.label}>Telegram API URL</Text>
          <TextInput
            style={styles.input}
            value={apiUrl}
            onChangeText={setApiUrl}
            autoCapitalize="none"
            placeholder="https://api.telegram.org"
            placeholderTextColor={colors.muted}
          />
        </>
      )}

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
  row: { flexDirection: "row", gap: 8, marginBottom: 12 },
  chip: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 8,
    paddingVertical: 8,
    paddingHorizontal: 12,
  },
  chipActive: { borderColor: colors.primary, backgroundColor: colors.primary },
  chipText: { color: colors.text, fontSize: 13, fontWeight: "600" },
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
