# ThreatSense 2.0 - Setup Guide

## Overview
ThreatSense is a lightweight automated security platform offering SOCaaS, PTaaS, and Vulnerability Scanning for small businesses.

## Fixed Issues

### Backend (API)
1. **Missing API Routers** - Created all required router files:
   - `/app/routers/health.py` - Health check endpoint
   - `/app/routers/auth.py` - Authentication with JWT tokens
   - `/app/routers/assets.py` - Asset management
   - `/app/routers/scans.py` - Scan management
   - `/app/routers/soc.py` - SOC alerts and dashboard
   - `/app/routers/admin_onboarding.py` - Customer onboarding
   - `/app/routers/invite_claim.py` - Invitation system

2. **Duplicate FastAPI Initialization** - Fixed duplicate `app = FastAPI()` in main.py

3. **Authentication System** - Implemented JWT-based authentication with bcrypt password hashing

### Frontend (Web)
1. **Duplicate Checkbox** - Removed duplicate "Requires approval" checkbox in dashboard
2. **Login Page** - Complete redesign with proper error handling and authentication flow
3. **UI Theme** - Created comprehensive blue/black cybersecurity theme:
   - Cyber grid background with animated scanner line
   - Glowing effects for primary elements
   - Professional color palette (blue: #0066FF, black: #000000)
   - Consistent component styling across all pages

4. **Updated All Pages**:
   - Home page with hero section and feature cards
   - Login page with proper form validation
   - Dashboard with stat cards and scan management
   - Assets page with asset creation and management
   - Findings page (placeholder for future development)

5. **Navigation Component** - Created reusable navigation with logout functionality

## Quick Start

### Prerequisites
- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- PostgreSQL (for production) or SQLite (for development)

### 1. Install Dependencies

#### Backend
```bash
cd apps/api
pip install -r requirements.txt
```

#### Frontend
```bash
cd apps/web
npm install
```

### 2. Start the API Server

```bash
cd apps/api
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### 3. Start the Frontend

```bash
cd apps/web
npm run dev
```

The web app will be available at `http://localhost:3000`

## Default Credentials

**Email:** demo@threatsense.com
**Password:** demo123

## API Endpoints

### Authentication
- `POST /auth/login` - Login with email/password, returns JWT token
- `GET /auth/me` - Get current user info

### Assets
- `GET /assets` - List all assets
- `POST /assets` - Create new asset
- `GET /assets/{id}` - Get specific asset

### Scans
- `GET /scans` - List all scans
- `POST /scans` - Create new scan
- `GET /scans/{id}` - Get specific scan
- `POST /scans/{id}/approve` - Approve a scan

### Health
- `GET /health` - API health check

## Project Structure

```
ThreatSense-2.0-main/
├── apps/
│   ├── api/                  # FastAPI backend
│   │   ├── app/
│   │   │   ├── routers/      # API endpoints
│   │   │   ├── db/           # Database utilities
│   │   │   └── main.py       # FastAPI app
│   │   └── requirements.txt
│   │
│   ├── web/                  # Next.js frontend
│   │   ├── src/
│   │   │   ├── app/          # Pages (App Router)
│   │   │   ├── components/   # Reusable components
│   │   │   ├── lib/          # Utilities
│   │   │   └── styles/       # Theme and styles
│   │   └── package.json
│   │
│   └── worker/               # Background job workers
│       ├── tasks/
│       ├── plugins/
│       └── worker.py
│
└── SETUP.md                  # This file
```

## Features

### SOCaaS (Security Operations Center as a Service)
- Automated threat detection
- Real-time security monitoring
- Alert management and response

### PTaaS (Penetration Testing as a Service)
- Automated security testing
- Vulnerability assessment
- Compliance reporting

### Vulnerability Scanning
- Nuclei-based scanning
- Custom scan parameters
- Multiple severity levels (Critical, High, Medium, Low)
- Configurable scan presets

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLModel** - SQL database ORM
- **PostgreSQL** - Primary database
- **JWT** - Authentication tokens
- **Bcrypt** - Password hashing

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **CSS-in-JS** - Inline styles with theme system

### Security Tools
- **Nuclei** - Vulnerability scanner
- **Nmap** - Network scanner (stub implementation)

## Development Notes

### Mock Data
The current implementation uses in-memory mock databases for rapid development:
- `MOCK_USERS` in `auth.py`
- `MOCK_ASSETS_DB` in `assets.py`
- `MOCK_SCANS_DB` in `scans.py`

**For production:** Replace these with actual database models using SQLModel/SQLAlchemy.

### Security Considerations
1. Change the `SECRET_KEY` in `auth.py` before deploying to production
2. Use environment variables for sensitive configuration
3. Implement proper CORS settings for your domain
4. Add rate limiting to prevent abuse
5. Enable HTTPS in production

## Deployment

### Frontend (Vercel)
The frontend is configured for Vercel deployment:
```bash
npm run build
```

Update CORS settings in `apps/api/app/main.py` with your Vercel domain.

### Backend (Docker/Cloud)
The backend can be deployed using Docker or any Python hosting service:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Next Steps

1. **Database Integration** - Replace mock data with PostgreSQL/SQLModel
2. **Worker Implementation** - Connect background workers for actual scanning
3. **Findings Page** - Build out the findings aggregation and display
4. **User Management** - Add user registration and multi-tenancy
5. **Real Scanning** - Integrate actual Nuclei/Nmap scanning
6. **Notifications** - Email/Slack alerts for critical findings
7. **Reporting** - PDF/CSV export of scan results
8. **Billing Integration** - Stripe/PayPal for subscriptions

## Support

For issues or questions:
- Check the API docs at `/docs`
- Review the code comments
- Test with the demo credentials

## Color Palette

### Primary Colors
- **Primary Blue**: #0066FF
- **Accent Cyan**: #00FFFF
- **Background Black**: #000000

### Status Colors
- **Critical**: #ff0066
- **High**: #ff6600
- **Medium**: #ffaa00
- **Low**: #ffdd00
- **Success**: #00ff88
- **Error**: #ff3366

## License

Built for Syracuse University EEE Entrepreneurship Class
