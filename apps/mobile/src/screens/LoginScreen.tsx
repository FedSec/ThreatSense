import { useState } from "react";
import {
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { apiFetch, setToken } from "../api";
import { colors } from "../theme";

export default function LoginScreen({
  onSuccess,
  onRegister,
}: {
  onSuccess: () => void;
  onRegister: () => void;
}) {
  const [email, setEmail] = useState("demo@threatsense.com");
  const [password, setPassword] = useState("demo123");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  async function login() {
    setLoading(true);
    setErr("");
    try {
      const data = await apiFetch("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      await setToken(data.access_token);
      onSuccess();
    } catch (e: any) {
      setErr(e.message || "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.brand}>THREATSENSE</Text>
      <Text style={styles.sub}>Security Platform</Text>
      {!!err && <Text style={styles.err}>{err}</Text>}
      <TextInput
        style={styles.input}
        autoCapitalize="none"
        keyboardType="email-address"
        placeholder="Email"
        placeholderTextColor={colors.muted}
        value={email}
        onChangeText={setEmail}
      />
      <TextInput
        style={styles.input}
        secureTextEntry
        placeholder="Password"
        placeholderTextColor={colors.muted}
        value={password}
        onChangeText={setPassword}
      />
      <Pressable style={styles.btn} onPress={login} disabled={loading}>
        <Text style={styles.btnText}>{loading ? "..." : "SIGN IN"}</Text>
      </Pressable>
      <Pressable onPress={onRegister}>
        <Text style={styles.link}>Create an account</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, justifyContent: "center", backgroundColor: colors.bg },
  brand: {
    color: colors.primary,
    fontSize: 32,
    fontWeight: "700",
    textAlign: "center",
    letterSpacing: 2,
  },
  sub: { color: colors.muted, textAlign: "center", marginBottom: 28, letterSpacing: 2 },
  input: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 8,
    color: colors.text,
    padding: 14,
    marginBottom: 12,
  },
  btn: {
    backgroundColor: colors.primary,
    padding: 14,
    borderRadius: 8,
    alignItems: "center",
    marginTop: 8,
  },
  btnText: { color: colors.text, fontWeight: "700" },
  link: { color: colors.primary, textAlign: "center", marginTop: 20 },
  err: { color: colors.danger, marginBottom: 12, textAlign: "center" },
});
