# ThreatSense Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                              │
│                     http://localhost:3000                        │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ HTTP/HTTPS
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│                    NEXT.JS FRONTEND                              │
│  ┌────────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │   Login    │  │Dashboard │  │  Assets  │  │ Findings │     │
│  │   Page     │  │   Page   │  │   Page   │  │   Page   │     │
│  └────────────┘  └──────────┘  └──────────┘  └──────────┘     │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Navigation Component                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Theme System (colors, styles, globals.css)        │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ REST API Calls
                        │ JSON over HTTP
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│                   FASTAPI BACKEND                                │
│                  http://localhost:8000                           │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    CORS Middleware                        │  │
│  │          (Allows requests from frontend)                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   /auth     │  │   /assets   │  │   /scans    │            │
│  │   Router    │  │   Router    │  │   Router    │            │
│  │             │  │             │  │             │            │
│  │ - login     │  │ - list      │  │ - list      │            │
│  │ - me        │  │ - create    │  │ - create    │            │
│  │             │  │ - get one   │  │ - get one   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │    /soc     │  │   /admin    │  │  /invite    │            │
│  │   Router    │  │   Router    │  │   Router    │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        │ Data Access
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│                    DATA LAYER (Current: Mock)                    │
│                   (Future: PostgreSQL + SQLModel)                │
│                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐│
│  │   MOCK_USERS     │  │  MOCK_ASSETS_DB  │  │ MOCK_SCANS_DB ││
│  │                  │  │                  │  │               ││
│  │ - email          │  │ - id             │  │ - id          ││
│  │ - password       │  │ - kind           │  │ - status      ││
│  │ - customer_id    │  │ - value          │  │ - scan_type   ││
│  │                  │  │ - verified       │  │ - plugin      ││
│  └──────────────────┘  └──────────────────┘  └───────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Authentication Flow

```
1. User enters credentials on Login Page
   │
   ▼
2. POST /auth/login (email, password)
   │
   ▼
3. Backend validates credentials
   - Check if email exists in MOCK_USERS
   - Verify password with bcrypt
   │
   ▼
4. Generate JWT token
   - Include email and customer_id in payload
   - Set expiration (24 hours)
   │
   ▼
5. Return token to frontend
   │
   ▼
6. Frontend stores token in localStorage
   │
   ▼
7. Redirect to Dashboard
   │
   ▼
8. All future requests include token in Authorization header
```

### Asset Creation Flow

```
1. User fills out asset form (kind, value)
   │
   ▼
2. POST /assets (kind, value)
   │
   ▼
3. Backend creates asset object
   - Generate UUID
   - Set verified = false
   │
   ▼
4. Add to MOCK_ASSETS_DB
   │
   ▼
5. Return created asset to frontend
   │
   ▼
6. Frontend adds to local state
   │
   ▼
7. Table updates automatically
```

### Scan Creation Flow

```
1. User selects asset and scan parameters
   │
   ▼
2. POST /scans (asset_id, scan_type, plugin, parameters)
   │
   ▼
3. Backend creates scan object
   - Generate UUID
   - Set status based on requires_approval
   - Store parameters
   │
   ▼
4. Add to MOCK_SCANS_DB
   │
   ▼
5. Return created scan to frontend
   │
   ▼
6. (Future) Trigger background worker
   │
   ▼
7. Frontend refreshes scan list
   │
   ▼
8. New scan appears in Recent Scans table
```

---

## Component Hierarchy

```
RootLayout (layout.tsx)
│
├── globals.css (cyber theme)
│
└── Pages
    │
    ├── HomePage (/)
    │   ├── Hero section
    │   ├── Feature cards
    │   └── CTA buttons
    │
    ├── LoginPage (/login)
    │   ├── Login form
    │   ├── Error display
    │   └── Demo credentials notice
    │
    ├── DashboardPage (/dashboard)
    │   ├── Navigation
    │   ├── Stats cards
    │   ├── Scan creation form
    │   └── Recent scans table
    │
    ├── AssetsPage (/assets)
    │   ├── Navigation
    │   ├── Add asset form
    │   ├── Scan settings
    │   └── Assets table
    │
    └── FindingsPage (/findings)
        ├── Navigation
        └── Coming soon content
```

---

## API Endpoints

### Authentication (`/auth`)
```
POST /auth/login
  Request:  { email, password }
  Response: { access_token, token_type }

GET /auth/me
  Headers:  Authorization: Bearer <token>
  Response: { email, full_name }
```

### Assets (`/assets`)
```
GET /assets
  Headers:  Authorization: Bearer <token>
  Response: [{ id, kind, value, verified }, ...]

POST /assets
  Headers:  Authorization: Bearer <token>
  Request:  { kind, value }
  Response: { id, kind, value, verified }

GET /assets/{id}
  Headers:  Authorization: Bearer <token>
  Response: { id, kind, value, verified }
```

### Scans (`/scans`)
```
GET /scans
  Headers:  Authorization: Bearer <token>
  Response: [{ id, status, scan_type, plugin }, ...]

POST /scans
  Headers:  Authorization: Bearer <token>
  Request:  { asset_id, scan_type, plugin, requires_approval, parameters }
  Response: { id, status, scan_type, plugin, created_at, updated_at }

GET /scans/{id}
  Headers:  Authorization: Bearer <token>
  Response: { id, status, scan_type, plugin, created_at, updated_at }

POST /scans/{id}/approve
  Headers:  Authorization: Bearer <token>
  Response: { message }
```

### Health (`/health`)
```
GET /health
  Response: { status, service }
```

---

## Security Architecture

### Authentication
```
┌─────────────────────────────────────────────────────┐
│  1. User submits credentials                         │
│     (email + password)                              │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  2. Backend verifies password                        │
│     bcrypt.verify(plain_password, hashed_password)  │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  3. Generate JWT token                              │
│     jwt.encode({                                     │
│       sub: email,                                    │
│       customer_id: id,                               │
│       exp: now + 24h                                │
│     }, SECRET_KEY)                                   │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  4. Client stores token                             │
│     localStorage.setItem("ts_token", token)         │
└───────────────┬─────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────┐
│  5. All requests include token                      │
│     Authorization: Bearer <token>                   │
└─────────────────────────────────────────────────────┘
```

### CORS Configuration
```
Allowed Origins:
  - http://localhost:3000      (development)
  - http://127.0.0.1:3000     (development)
  - https://your-domain.com    (production)

Allowed Methods: *
Allowed Headers: *
Allow Credentials: true
```

---

## Technology Stack Details

### Frontend Stack
```
Next.js 14
├── React 18.3.1
├── TypeScript 5.9.3
└── App Router
    ├── Server Components (layout)
    └── Client Components (pages)
```

### Backend Stack
```
FastAPI 0.115.6
├── Uvicorn (ASGI server)
├── Pydantic (validation)
├── Python-Jose (JWT)
├── Passlib + Bcrypt (passwords)
└── SQLModel (future DB layer)
```

### Development Tools
```
├── TypeScript LSP
├── Python Language Server
├── Hot Module Replacement
└── Auto-reload on changes
```

---

## File Structure

```
ThreatSense-main/
│
├── apps/
│   │
│   ├── api/                           # Backend
│   │   ├── app/
│   │   │   ├── routers/              # API endpoints
│   │   │   │   ├── __init__.py
│   │   │   │   ├── health.py         # Health check
│   │   │   │   ├── auth.py           # Authentication
│   │   │   │   ├── assets.py         # Asset management
│   │   │   │   ├── scans.py          # Scan management
│   │   │   │   ├── soc.py            # SOC features
│   │   │   │   ├── admin_onboarding.py
│   │   │   │   └── invite_claim.py
│   │   │   │
│   │   │   ├── db/                   # Database
│   │   │   │   ├── session.py
│   │   │   │   ├── init_db.py
│   │   │   │   └── seed_customer.py
│   │   │   │
│   │   │   └── main.py               # FastAPI app
│   │   │
│   │   └── requirements.txt
│   │
│   ├── web/                           # Frontend
│   │   ├── src/
│   │   │   ├── app/                  # Pages
│   │   │   │   ├── layout.tsx        # Root layout
│   │   │   │   ├── globals.css       # Global styles
│   │   │   │   ├── page.tsx          # Home page
│   │   │   │   ├── login/
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── dashboard/
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── assets/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── findings/
│   │   │   │       └── page.tsx
│   │   │   │
│   │   │   ├── components/           # Reusable components
│   │   │   │   └── Navigation.tsx
│   │   │   │
│   │   │   ├── lib/                  # Utilities
│   │   │   │   ├── api.ts            # API client
│   │   │   │   └── auth.ts
│   │   │   │
│   │   │   └── styles/               # Theme
│   │   │       └── theme.ts          # Colors & styles
│   │   │
│   │   ├── public/                   # Static assets
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── next.config.js
│   │
│   └── worker/                        # Background jobs
│       ├── tasks/
│       ├── plugins/
│       └── worker.py
│
├── start-dev.sh                       # Quick start
├── README.md                          # Main docs
├── SETUP.md                           # Setup guide
├── CHANGES.md                         # Changelog
├── DEMO-GUIDE.md                      # Demo instructions
└── ARCHITECTURE.md                    # This file
```

---

## Future Architecture (Production)

```
┌─────────────────────────────────────────────────────────┐
│                  USERS (Multiple Tenants)                │
└────────────┬─────────────────────────────────┬──────────┘
             │                                 │
             ▼                                 ▼
┌────────────────────────┐      ┌────────────────────────┐
│   Web Browser          │      │   Mobile App (Future)  │
└────────┬───────────────┘      └────────┬───────────────┘
         │                                │
         └────────────┬───────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │    Load Balancer       │
         └────────┬───────────────┘
                  │
      ┌───────────┴───────────┐
      │                       │
      ▼                       ▼
┌────────────┐          ┌────────────┐
│  Next.js   │          │  Next.js   │
│ (Vercel)   │          │ (Replica)  │
└─────┬──────┘          └─────┬──────┘
      │                       │
      └───────────┬───────────┘
                  │
                  ▼
         ┌────────────────────┐
         │   API Gateway      │
         └────────┬───────────┘
                  │
      ┌───────────┴───────────┬─────────────┐
      │                       │             │
      ▼                       ▼             ▼
┌────────────┐         ┌────────────┐  ┌────────────┐
│  FastAPI   │         │  FastAPI   │  │  FastAPI   │
│  Instance  │         │  Instance  │  │  Instance  │
└─────┬──────┘         └─────┬──────┘  └─────┬──────┘
      │                      │               │
      └──────────┬───────────┴───────────────┘
                 │
                 ▼
      ┌─────────────────────┐
      │   PostgreSQL        │
      │   (Primary)         │
      └──────┬──────────────┘
             │
             ▼
      ┌─────────────────────┐
      │   PostgreSQL        │
      │   (Read Replica)    │
      └─────────────────────┘


             ┌───────────────┐
             │  Redis Cache  │
             └───────────────┘


      ┌──────────────────────┐
      │  Worker Queue        │
      │  (Celery/RabbitMQ)   │
      └──────┬───────────────┘
             │
             ▼
      ┌──────────────────────┐
      │  Scan Workers        │
      │  - Nuclei            │
      │  - Nmap              │
      │  - Custom plugins    │
      └──────────────────────┘
```

---

## Scaling Considerations

### Horizontal Scaling
- Multiple API instances behind load balancer
- Stateless design (JWT tokens)
- Database connection pooling
- Redis for session management

### Vertical Scaling
- Increase worker resources for scanning
- Optimize database queries
- CDN for static assets
- Caching layer

### Data Partitioning
- Customer data partitioned by customer_id
- Separate databases per region (future)
- Read replicas for reporting

---

This architecture is designed to start simple (current MVP) and scale to handle thousands of customers with minimal refactoring.
