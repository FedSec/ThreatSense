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

export default function RegisterScreen({
  onSuccess,
  onLogin,
}: {
  onSuccess: () => void;
  onLogin: () => void;
}) {
  const [fullName, setFullName] = useState("");
  const [company, setCompany] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  async function register() {
    setLoading(true);
    setErr("");
    try {
      const data = await apiFetch("/auth/register", {
        method: "POST",
        body: JSON.stringify({
          full_name: fullName,
          company_name: company,
          email,
          password,
        }),
      });
      await setToken(data.access_token);
      onSuccess();
    } catch (e: any) {
      setErr(e.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.brand}>CREATE ACCOUNT</Text>
      {!!err && <Text style={styles.err}>{err}</Text>}
      <TextInput style={styles.input} placeholder="Full name" placeholderTextColor={colors.muted} value={fullName} onChangeText={setFullName} />
      <TextInput style={styles.input} placeholder="Company" placeholderTextColor={colors.muted} value={company} onChangeText={setCompany} />
      <TextInput style={styles.input} autoCapitalize="none" keyboardType="email-address" placeholder="Email" placeholderTextColor={colors.muted} value={email} onChangeText={setEmail} />
      <TextInput style={styles.input} secureTextEntry placeholder="Password" placeholderTextColor={colors.muted} value={password} onChangeText={setPassword} />
      <Pressable style={styles.btn} onPress={register} disabled={loading}>
        <Text style={styles.btnText}>{loading ? "..." : "REGISTER"}</Text>
      </Pressable>
      <Pressable onPress={onLogin}>
        <Text style={styles.link}>Back to sign in</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, justifyContent: "center", backgroundColor: colors.bg },
  brand: { color: colors.primary, fontSize: 24, fontWeight: "700", textAlign: "center", marginBottom: 24 },
  input: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 8,
    color: colors.text,
    padding: 14,
    marginBottom: 12,
  },
  btn: { backgroundColor: colors.primary, padding: 14, borderRadius: 8, alignItems: "center" },
  btnText: { color: colors.text, fontWeight: "700" },
  link: { color: colors.primary, textAlign: "center", marginTop: 20 },
  err: { color: colors.danger, marginBottom: 12, textAlign: "center" },
});
