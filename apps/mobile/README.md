# ThreatSense Mobile (Expo)

React Native app consuming the ThreatSense REST API.

## Setup

```bash
cd apps/mobile
npm install
EXPO_PUBLIC_API_BASE=http://localhost:8000 npm start
```

On a physical device, set `EXPO_PUBLIC_API_BASE` to your machine's LAN IP (e.g. `http://192.168.1.10:8000`).

## Screens

- Login / Register
- Dashboard (counts + recent scans)
- Assets (add + start Nuclei scan)
- Findings (list, detail, status update)
- Settings (email or Telegram + Slack/Discord webhooks)
- Billing (Stripe Checkout or local plan upgrade)
