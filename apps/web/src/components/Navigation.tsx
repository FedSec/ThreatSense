"use client";
import { usePathname } from "next/navigation";
import { colors, styles } from "@/styles/theme";

export default function Navigation() {
  const pathname = usePathname();

  const links = [
    { href: "/dashboard", label: "Dashboard" },
    { href: "/assets", label: "Assets" },
    { href: "/findings", label: "Findings" },
  ];

  function logout() {
    localStorage.removeItem("ts_token");
    window.location.href = "/login";
  }

  return (
    <nav style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      marginBottom: "32px",
      padding: "16px 0",
      borderBottom: `2px solid ${colors.borderPrimary}`,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: "24px" }}>
        <h2 style={{
          fontSize: "24px",
          fontWeight: 700,
          color: colors.primary,
          margin: 0,
          textShadow: `0 0 10px rgba(0, 102, 255, 0.5)`,
          letterSpacing: "1px",
        }}>
          THREATSENSE
        </h2>

        <div style={styles.nav}>
          {links.map((link) => (
            <a
              key={link.href}
              href={link.href}
              style={{
                ...styles.navLink,
                ...(pathname === link.href ? styles.navLinkActive : {}),
              }}
            >
              {link.label}
            </a>
          ))}
        </div>
      </div>

      <button
        onClick={logout}
        style={{
          ...styles.buttonSecondary,
          padding: "8px 16px",
          fontSize: "12px",
        }}
      >
        LOGOUT
      </button>
    </nav>
  );
}
