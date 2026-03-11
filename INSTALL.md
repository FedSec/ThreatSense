# ThreatSense Installation Guide

Complete setup guide for getting ThreatSense running with PostgreSQL and real Nuclei scanning.

---

## Quick Start (5 minutes)

### Option 1: With PostgreSQL (Recommended)

```bash
# 1. Start PostgreSQL
docker-compose up -d

# 2. Copy environment file
cp .env.example .env

# 3. Install Python dependencies
cd apps/api
pip install -r requirements.txt

# 4. Install Node dependencies
cd ../web
npm install

# 5. Start the application
cd ../..
./start-dev.sh
```

### Option 2: SQLite (No Docker needed)

```bash
# 1. Update .env to use SQLite
echo "DATABASE_URL=sqlite:///./threatsense.db" > .env

# 2. Install Python dependencies
cd apps/api
pip install -r requirements.txt

# 3. Install Node dependencies
cd ../web
npm install

# 4. Start the application
cd ../..
./start-dev.sh
```

---

## Detailed Setup

### Prerequisites

**Required:**
- Python 3.11+
- Node.js 18+
- npm or yarn

**Optional (for production features):**
- Docker & Docker Compose (for PostgreSQL)
- Nuclei (for real vulnerability scanning)
- Go 1.20+ (to install Nuclei)

---

## 1. Database Setup

### Option A: PostgreSQL with Docker (Recommended)

```bash
# Start PostgreSQL container
docker-compose up -d

# Verify it's running
docker ps

# Check logs if needed
docker logs threatsense-db

# Connect to database (optional)
docker exec -it threatsense-db psql -U threatsense
```

The database will be available at:
- **Host**: localhost
- **Port**: 5432
- **Database**: threatsense
- **User**: threatsense
- **Password**: threatsense_password

### Option B: PostgreSQL Manual Install

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo -u postgres psql

# In psql:
CREATE DATABASE threatsense;
CREATE USER threatsense WITH ENCRYPTED PASSWORD 'threatsense_password';
GRANT ALL PRIVILEGES ON DATABASE threatsense TO threatsense;
\q
```

**On macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
createdb threatsense
```

### Option C: SQLite (Development Only)

Update `.env`:
```bash
DATABASE_URL=sqlite:///./threatsense.db
```

---

## 2. Nuclei Scanner Setup (Optional but Recommended)

Nuclei enables real vulnerability scanning. Without it, the platform will use mock findings for demo purposes.

### Install Nuclei

**Option 1: Using Go (Recommended)**
```bash
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# Verify installation
nuclei -version

# Update templates
nuclei -update-templates
```

**Option 2: Binary Download**
```bash
# Linux
wget https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_3.0.0_linux_amd64.zip
unzip nuclei_3.0.0_linux_amd64.zip
sudo mv nuclei /usr/local/bin/
chmod +x /usr/local/bin/nuclei

# macOS
brew install nuclei
```

**Option 3: Docker**
```bash
docker pull projectdiscovery/nuclei:latest

# Run a test scan
docker run projectdiscovery/nuclei -target https://example.com
```

### Verify Nuclei

```bash
nuclei -version
# Should output: Nuclei v3.x.x

# Test scan
nuclei -target https://example.com -silent
```

---

## 3. Backend Setup

```bash
cd apps/api

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file if not done already
cp ../../.env.example ../../.env

# Initialize database (creates tables and demo account)
python -c "from app.database import init_db; init_db()"

# Start the API server
uvicorn app.main:app --reload --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

---

## 4. Frontend Setup

```bash
cd apps/web

# Install dependencies
npm install

# Start development server
npm run dev
```

The web app will be available at:
- **App**: http://localhost:3000

---

## 5. Verify Installation

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@threatsense.com","password":"demo123"}'
```

### Test the Web App

1. Open http://localhost:3000
2. Click "GET STARTED"
3. Login with:
   - Email: demo@threatsense.com
   - Password: demo123
4. Create an asset
5. Run a scan
6. View findings

---

## 6. Running Scans

### With Nuclei Installed

Scans will automatically use real Nuclei templates and return actual vulnerabilities.

### Without Nuclei

The system will generate realistic demo findings for testing purposes.

---

## Environment Variables

Create a `.env` file in the project root:

```bash
# Database
DATABASE_URL=postgresql://threatsense:threatsense_password@localhost:5432/threatsense

# Security
SECRET_KEY=your-secret-key-change-in-production

# API
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
NEXT_PUBLIC_API_BASE=http://localhost:8000

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

---

## Troubleshooting

### Database Connection Error

**Problem**: `connection refused` or `database does not exist`

**Solution**:
```bash
# Check if PostgreSQL is running
docker ps  # or: sudo service postgresql status

# Restart PostgreSQL
docker-compose down && docker-compose up -d

# Recreate database
docker exec -it threatsense-db psql -U threatsense -c "DROP DATABASE IF EXISTS threatsense; CREATE DATABASE threatsense;"
```

### Nuclei Not Found

**Problem**: `Nuclei not found. Install with: go install...`

**Solution**:
```bash
# Install Nuclei
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# Add to PATH
export PATH=$PATH:$HOME/go/bin

# Verify
which nuclei
```

### Port Already in Use

**Problem**: `Address already in use`

**Solution**:
```bash
# Find process using port 8000
lsof -ti:8000 | xargs kill -9

# Find process using port 3000
lsof -ti:3000 | xargs kill -9

# Or use different ports
uvicorn app.main:app --port 8001
npm run dev -- -p 3001
```

### Frontend Can't Connect to API

**Problem**: CORS error or connection refused

**Solution**:
1. Verify API is running: `curl http://localhost:8000/health`
2. Check CORS settings in `apps/api/app/main.py`
3. Verify `NEXT_PUBLIC_API_BASE` in frontend

---

## Production Deployment

### 1. Update Environment Variables

```bash
# Use strong secret key
SECRET_KEY=$(openssl rand -hex 32)

# Use production database URL
DATABASE_URL=postgresql://user:pass@your-db-host:5432/threatsense

# Update allowed origins
ALLOWED_ORIGINS=https://yourdomain.com
```

### 2. Deploy Backend

**Option A: Docker**
```bash
cd apps/api
docker build -t threatsense-api .
docker run -p 8000:8000 --env-file .env threatsense-api
```

**Option B: Traditional Hosting**
```bash
pip install -r requirements.txt
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 3. Deploy Frontend

**Option A: Vercel (Recommended)**
```bash
cd apps/web
npm install -g vercel
vercel
```

**Option B: Docker**
```bash
cd apps/web
docker build -t threatsense-web .
docker run -p 3000:3000 threatsense-web
```

---

## Next Steps

1. ✅ **Test the Platform**: Create assets, run scans, view findings
2. ✅ **Install Nuclei**: For real vulnerability scanning
3. ✅ **Secure the Installation**: Change SECRET_KEY, use HTTPS
4. ✅ **Read the Docs**: Check PRODUCT-BRIEF.md for business info
5. ✅ **Deploy to Production**: Follow DEPLOYMENT-CHECKLIST.md

---

## Support

- **Documentation**: See README.md, SETUP.md, ARCHITECTURE.md
- **API Docs**: http://localhost:8000/docs
- **Issues**: Report bugs on GitHub
- **Demo**: Use demo@threatsense.com / demo123

---

## Quick Commands Reference

```bash
# Start everything
./start-dev.sh

# Start PostgreSQL only
docker-compose up -d

# Stop PostgreSQL
docker-compose down

# Reset database
docker-compose down -v && docker-compose up -d

# Run API manually
cd apps/api && uvicorn app.main:app --reload

# Run frontend manually
cd apps/web && npm run dev

# Install Nuclei
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# Update Nuclei templates
nuclei -update-templates

# Test scan
nuclei -target https://example.com -silent -severity high,critical
```

---

**You're all set! 🚀**

Open http://localhost:3000 and start securing your digital assets!
