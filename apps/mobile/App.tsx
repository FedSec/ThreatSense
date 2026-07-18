import { StatusBar } from "expo-status-bar";
import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  SafeAreaView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { clearToken, getToken } from "./src/api";
import AssetsScreen from "./src/screens/AssetsScreen";
import BillingScreen from "./src/screens/BillingScreen";
import DashboardScreen from "./src/screens/DashboardScreen";
import FindingsScreen from "./src/screens/FindingsScreen";
import LoginScreen from "./src/screens/LoginScreen";
import RegisterScreen from "./src/screens/RegisterScreen";
import SettingsScreen from "./src/screens/SettingsScreen";
import { colors } from "./src/theme";

type Screen =
  | "login"
  | "register"
  | "dashboard"
  | "assets"
  | "findings"
  | "settings"
  | "billing";

export default function App() {
  const [screen, setScreen] = useState<Screen>("login");
  const [booting, setBooting] = useState(true);

  useEffect(() => {
    getToken().then((t) => {
      setScreen(t ? "dashboard" : "login");
      setBooting(false);
    });
  }, []);

  async function logout() {
    await clearToken();
    setScreen("login");
  }

  if (booting) {
    return (
      <View style={styles.boot}>
        <ActivityIndicator color={colors.primary} size="large" />
      </View>
    );
  }

  const nav = {
    go: setScreen,
    logout,
  };

  return (
    <SafeAreaProvider>
      <SafeAreaView style={styles.root}>
        <StatusBar style="light" />
        {screen === "login" && (
          <LoginScreen
            onSuccess={() => setScreen("dashboard")}
            onRegister={() => setScreen("register")}
          />
        )}
        {screen === "register" && (
          <RegisterScreen
            onSuccess={() => setScreen("dashboard")}
            onLogin={() => setScreen("login")}
          />
        )}
        {screen === "dashboard" && <DashboardScreen nav={nav} />}
        {screen === "assets" && <AssetsScreen nav={nav} />}
        {screen === "findings" && <FindingsScreen nav={nav} />}
        {screen === "settings" && <SettingsScreen nav={nav} />}
        {screen === "billing" && <BillingScreen nav={nav} />}
      </SafeAreaView>
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.bg },
  boot: {
    flex: 1,
    backgroundColor: colors.bg,
    alignItems: "center",
    justifyContent: "center",
  },
});
