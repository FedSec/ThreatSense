import { Pressable, StyleSheet, Text, View } from "react-native";
import { colors } from "../theme";

type Props = {
  current: string;
  onNavigate: (screen: any) => void;
  onLogout: () => void;
};

const LINKS = [
  { id: "dashboard", label: "Home" },
  { id: "assets", label: "Assets" },
  { id: "findings", label: "Findings" },
  { id: "settings", label: "Settings" },
  { id: "billing", label: "Billing" },
];

export default function NavBar({ current, onNavigate, onLogout }: Props) {
  return (
    <View style={styles.wrap}>
      <Text style={styles.brand}>THREATSENSE</Text>
      <View style={styles.row}>
        {LINKS.map((l) => (
          <Pressable key={l.id} onPress={() => onNavigate(l.id)}>
            <Text style={[styles.link, current === l.id && styles.active]}>
              {l.label}
            </Text>
          </Pressable>
        ))}
        <Pressable onPress={onLogout}>
          <Text style={styles.logout}>Logout</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    borderBottomWidth: 2,
    borderBottomColor: colors.primary,
    paddingBottom: 12,
    marginBottom: 16,
  },
  brand: {
    color: colors.primary,
    fontSize: 20,
    fontWeight: "700",
    letterSpacing: 1,
    marginBottom: 10,
  },
  row: { flexDirection: "row", flexWrap: "wrap", gap: 12 },
  link: { color: colors.muted, fontSize: 13 },
  active: { color: colors.primary, fontWeight: "700" },
  logout: { color: colors.danger, fontSize: 13 },
});
