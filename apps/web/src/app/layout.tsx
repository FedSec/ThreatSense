import type { ReactNode } from "react";
import "./globals.css";

export const metadata = {
  title: "ThreatSense - Automated Security Platform",
  description: "Lightweight SOCaaS, PTaaS, and Vulnerability Scanning for Small Businesses",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="cyber-bg">
        {children}
      </body>
    </html>
  );
}
