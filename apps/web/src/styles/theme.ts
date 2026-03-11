import { CSSProperties } from "react";

// ThreatSense Color Palette
export const colors = {
  // Primary
  primary: "#0066FF",
  primaryDark: "#0052CC",
  primaryLight: "#3385FF",

  // Accent
  accent: "#00FFFF",
  accentDark: "#00CCCC",

  // Background
  bgPrimary: "#000000",
  bgSecondary: "#0a0a0f",
  bgTertiary: "#151520",
  bgCard: "#1a1a2e",

  // Border
  borderPrimary: "#0066FF",
  borderSecondary: "#2a2a3e",
  borderAccent: "#00FFFF",

  // Text
  textPrimary: "#ffffff",
  textSecondary: "#b0b0c0",
  textMuted: "#666680",

  // Status
  success: "#00ff88",
  warning: "#ffaa00",
  error: "#ff3366",
  info: "#0099ff",

  // Semantic
  critical: "#ff0066",
  high: "#ff6600",
  medium: "#ffaa00",
  low: "#ffdd00",
};

// Common component styles
export const styles = {
  // Layout
  container: {
    padding: "24px",
    maxWidth: "1400px",
    margin: "0 auto",
  } as CSSProperties,

  // Cards
  card: {
    background: `linear-gradient(135deg, ${colors.bgCard} 0%, ${colors.bgTertiary} 100%)`,
    border: `1px solid ${colors.borderSecondary}`,
    borderRadius: "12px",
    padding: "20px",
    position: "relative",
    overflow: "hidden",
  } as CSSProperties,

  cardGlow: {
    background: `linear-gradient(135deg, ${colors.bgCard} 0%, ${colors.bgTertiary} 100%)`,
    border: `1px solid ${colors.borderPrimary}`,
    borderRadius: "12px",
    padding: "20px",
    position: "relative",
    overflow: "hidden",
    boxShadow: `0 0 20px rgba(0, 102, 255, 0.3), 0 0 40px rgba(0, 102, 255, 0.1)`,
  } as CSSProperties,

  // Inputs
  input: {
    width: "100%",
    padding: "12px 16px",
    background: colors.bgSecondary,
    border: `1px solid ${colors.borderSecondary}`,
    borderRadius: "8px",
    color: colors.textPrimary,
    fontSize: "14px",
    outline: "none",
    transition: "all 0.3s ease",
  } as CSSProperties,

  inputFocus: {
    borderColor: colors.borderPrimary,
    boxShadow: `0 0 10px rgba(0, 102, 255, 0.3)`,
  } as CSSProperties,

  select: {
    width: "100%",
    padding: "12px 16px",
    background: colors.bgSecondary,
    border: `1px solid ${colors.borderSecondary}`,
    borderRadius: "8px",
    color: colors.textPrimary,
    fontSize: "14px",
    outline: "none",
    cursor: "pointer",
  } as CSSProperties,

  textarea: {
    width: "100%",
    padding: "12px 16px",
    background: colors.bgSecondary,
    border: `1px solid ${colors.borderSecondary}`,
    borderRadius: "8px",
    color: colors.textPrimary,
    fontSize: "14px",
    fontFamily: "monospace",
    outline: "none",
    resize: "vertical",
    minHeight: "120px",
  } as CSSProperties,

  // Buttons
  button: {
    padding: "12px 24px",
    background: `linear-gradient(135deg, ${colors.primary} 0%, ${colors.primaryDark} 100%)`,
    border: `1px solid ${colors.borderPrimary}`,
    borderRadius: "8px",
    color: colors.textPrimary,
    fontSize: "14px",
    fontWeight: 600,
    cursor: "pointer",
    outline: "none",
    transition: "all 0.3s ease",
    boxShadow: `0 0 15px rgba(0, 102, 255, 0.4)`,
  } as CSSProperties,

  buttonSecondary: {
    padding: "12px 24px",
    background: "transparent",
    border: `1px solid ${colors.borderPrimary}`,
    borderRadius: "8px",
    color: colors.primary,
    fontSize: "14px",
    fontWeight: 600,
    cursor: "pointer",
    outline: "none",
    transition: "all 0.3s ease",
  } as CSSProperties,

  buttonDanger: {
    padding: "12px 24px",
    background: `linear-gradient(135deg, ${colors.error} 0%, #cc0044 100%)`,
    border: `1px solid ${colors.error}`,
    borderRadius: "8px",
    color: colors.textPrimary,
    fontSize: "14px",
    fontWeight: 600,
    cursor: "pointer",
    outline: "none",
    transition: "all 0.3s ease",
  } as CSSProperties,

  // Labels
  label: {
    display: "block",
    fontSize: "12px",
    fontWeight: 600,
    color: colors.textSecondary,
    marginBottom: "8px",
    textTransform: "uppercase",
    letterSpacing: "0.5px",
  } as CSSProperties,

  // Tables
  table: {
    width: "100%",
    borderCollapse: "separate",
    borderSpacing: "0",
    background: colors.bgCard,
    borderRadius: "12px",
    overflow: "hidden",
  } as CSSProperties,

  tableHeader: {
    background: colors.bgSecondary,
    borderBottom: `2px solid ${colors.borderPrimary}`,
    textAlign: "left",
    padding: "14px 12px",
    fontSize: "12px",
    fontWeight: 600,
    color: colors.primary,
    textTransform: "uppercase",
    letterSpacing: "0.5px",
  } as CSSProperties,

  tableCell: {
    borderBottom: `1px solid ${colors.borderSecondary}`,
    padding: "14px 12px",
    fontSize: "14px",
    color: colors.textPrimary,
  } as CSSProperties,

  // Navigation
  nav: {
    display: "flex",
    gap: "16px",
    marginBottom: "24px",
  } as CSSProperties,

  navLink: {
    color: colors.textSecondary,
    textDecoration: "none",
    padding: "8px 16px",
    borderRadius: "6px",
    fontSize: "14px",
    fontWeight: 500,
    transition: "all 0.3s ease",
    border: `1px solid transparent`,
  } as CSSProperties,

  navLinkActive: {
    color: colors.primary,
    border: `1px solid ${colors.borderPrimary}`,
    background: colors.bgTertiary,
    boxShadow: `0 0 10px rgba(0, 102, 255, 0.2)`,
  } as CSSProperties,

  // Stat cards
  statCard: {
    background: `linear-gradient(135deg, ${colors.bgCard} 0%, ${colors.bgTertiary} 100%)`,
    border: `1px solid ${colors.borderPrimary}`,
    borderRadius: "12px",
    padding: "20px",
    position: "relative",
    overflow: "hidden",
  } as CSSProperties,

  statTitle: {
    fontSize: "12px",
    fontWeight: 600,
    color: colors.textSecondary,
    textTransform: "uppercase",
    letterSpacing: "0.5px",
    marginBottom: "8px",
  } as CSSProperties,

  statValue: {
    fontSize: "32px",
    fontWeight: 700,
    color: colors.primary,
    textShadow: `0 0 10px rgba(0, 102, 255, 0.5)`,
  } as CSSProperties,

  // Error/Success messages
  alert: {
    padding: "16px",
    borderRadius: "8px",
    marginBottom: "20px",
    fontSize: "14px",
  } as CSSProperties,

  alertError: {
    background: `${colors.error}22`,
    border: `1px solid ${colors.error}`,
    color: colors.error,
  } as CSSProperties,

  alertSuccess: {
    background: `${colors.success}22`,
    border: `1px solid ${colors.success}`,
    color: colors.success,
  } as CSSProperties,

  alertInfo: {
    background: `${colors.info}22`,
    border: `1px solid ${colors.info}`,
    color: colors.info,
  } as CSSProperties,
};
