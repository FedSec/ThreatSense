# ThreatSense 2.0

**Lightweight Automated Security Platform for Small Businesses**

ThreatSense provides enterprise-grade security services at an affordable price point, offering SOCaaS (Security Operations Center as a Service), PTaaS (Penetration Testing as a Service), and Vulnerability Scanning through an easy-to-use interface.

## 🎯 Project Overview

Built for Syracuse University's Entrepreneurial EEE class, ThreatSense addresses a critical market gap: small businesses that need cybersecurity protection but cannot afford full-scale enterprise solutions.

### Key Features

- **🛡️ SOCaaS** - Automated threat detection and security monitoring
- **🔍 PTaaS** - On-demand penetration testing and security assessments
- **⚡ Vulnerability Scanning** - Continuous scanning with Nuclei and custom plugins
- **📊 Real-time Dashboard** - Monitor your security posture at a glance
- **🎨 Modern UI** - Sleek blue/black cyber-themed interface
- **💰 Subscription Model** - Monthly/annual plans for predictable costs

## 🚀 Quick Start

### Option 1: Full stack with Docker (Recommended)

```bash
cp .env.example .env
docker compose up --build
```

This starts PostgreSQL, Redis, Mailpit (http://localhost:8025), API (8000), Celery worker (Nuclei), and the web app (3000).

### Option 2: Automated local script

```bash
./start-dev.sh
```

Requires Postgres + Redis running locally (or `docker compose up postgres redis mailpit -d`).

### Option 3: Manual Setup

**Infrastructure:**
```bash
docker compose up postgres redis mailpit -d
```

**Backend:**
```bash
cd apps/api
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

**Worker (separate terminal):**
```bash
cd apps/worker
pip install -r requirements.txt
celery -A worker.celery_app worker --loglevel=INFO
```

**Frontend:**
```bash
cd apps/web
npm install
npm run dev
```

**Mobile (Expo):**
```bash
cd apps/mobile
npm install
EXPO_PUBLIC_API_BASE=http://localhost:8000 npm start
```

## 🔐 Demo Credentials

**Email:** demo@threatsense.com
**Password:** demo123

## 📱 Access Points

- **Web App:** http://localhost:3000
- **API Server:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## 🎨 UI Theme

ThreatSense features a professional cybersecurity-themed interface with:
- **Primary Blue:** #0066FF (glowing accents)
- **Background:** Pure black (#000000) with cyber grid
- **Animated scanner lines** for that authentic security feel
- **Responsive design** that works on all devices

## 📋 What's Included

### Fixed & Implemented

✅ Complete authentication system with JWT tokens
✅ Asset management (domains, IPs, web apps, etc.)
✅ Scan creation and monitoring
✅ Blue/black cybersecurity UI theme
✅ Responsive navigation and layouts
✅ API documentation (FastAPI auto-docs)
✅ Mock database for rapid development
✅ Error handling and loading states

### Architecture

```
┌─────────────────┐
│   Next.js Web   │ ← React frontend with TypeScript
└────────┬────────┘
         │
    ┌────▼────┐
    │  CORS   │
    └────┬────┘
         │
┌────────▼────────┐
│  FastAPI Backend│ ← Python REST API
└────────┬────────┘
         │
    ┌────▼────┐
    │Database │ ← Currently in-memory, ready for PostgreSQL
    └─────────┘
```

## 🛠️ Tech Stack

**Frontend:**
- Next.js 14 (App Router)
- TypeScript
- CSS-in-JS with custom theme system

**Backend:**
- FastAPI (Python)
- JWT Authentication (customer-scoped multi-tenancy)
- Bcrypt password hashing
- SQLModel + PostgreSQL + Alembic
- Celery + Redis workers
- Stripe billing, SMTP email, Slack/Discord webhooks

**Security Tools:**
- Nuclei vulnerability scanner
- Nmap network scanner
- Custom plugin system

**Mobile:**
- Expo (React Native) + SecureStore auth

## 📊 Business Model

**Target Market:** Small businesses (10-100 employees) who need cybersecurity but lack budget for enterprise solutions

**Pricing Tiers:**
- **Starter:** $99/month - Basic vulnerability scanning
- **Professional:** $299/month - SOCaaS + scanning
- **Enterprise:** $599/month - Full PTaaS + SOCaaS + scanning

**Competitive Advantage:**
- Automated, reducing operational costs
- Self-service platform
- Transparent pricing
- Easy to understand reports

## 🔄 Development Roadmap

### Phase 1 (Current - MVP)
- [x] Core authentication
- [x] Asset management
- [x] Scan orchestration
- [x] Professional UI/UX
- [x] Basic API endpoints

### Phase 2 (Next Sprint)
- [x] PostgreSQL integration
- [x] Real Nuclei scanning integration
- [x] Findings aggregation
- [x] Email notifications
- [x] User registration

### Phase 3 (Future)
- [x] Multi-tenancy (multiple customers)
- [x] Stripe payment integration
- [x] Advanced reporting (PDF/CSV)
- [x] Slack/Discord integrations
- [x] Mobile app

## 📁 Project Structure

```
ThreatSense-main/
├── apps/
│   ├── api/                 # FastAPI backend
│   │   ├── app/
│   │   │   ├── routers/    # API endpoints
│   │   │   ├── db/         # Database setup
│   │   │   └── main.py     # App entry point
│   │   └── requirements.txt
│   │
│   ├── web/                # Next.js frontend
│   │   ├── src/
│   │   │   ├── app/        # Pages (App Router)
│   │   │   ├── components/ # Reusable UI components
│   │   │   ├── lib/        # API client, utilities
│   │   │   └── styles/     # Theme configuration
│   │   └── package.json
│   │
│   ├── worker/             # Celery + Nuclei scan workers
│   │   ├── tasks/
│   │   └── plugins/
│   │
│   └── mobile/             # Expo React Native app
│
├── docker-compose.yml      # Postgres, Redis, Mailpit, API, worker, web
├── start-dev.sh            # Quick start script
├── SETUP.md                # Detailed setup guide
└── README.md               # This file
```

## 🎓 Academic Context

This project was developed as part of Syracuse University's Entrepreneurial EEE class to demonstrate:
- Market research and problem identification
- MVP development and rapid prototyping
- Full-stack software architecture
- Cybersecurity domain expertise
- Business model design

## 🤝 Contributing

This is an academic project, but suggestions and improvements are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

Copyright © 2024 - Syracuse University EEE Class Project

## 🆘 Troubleshooting

**Port already in use?**
```bash
# Kill processes on ports 3000 and 8000
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

**Dependencies not installing?**
```bash
# Update pip
pip install --upgrade pip

# Clear npm cache
npm cache clean --force
```

**API not connecting?**
- Check that CORS is configured for localhost:3000
- Verify API_BASE in `apps/web/src/lib/api.ts`
- Check browser console for errors

## 📧 Contact

Built with ❤️ for small business security

---

**Remember:** This is a development version. For production deployment, update security keys, implement proper database, and enable HTTPS.
