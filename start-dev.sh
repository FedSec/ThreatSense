#!/bin/bash

# ThreatSense Development Startup Script

echo "========================================="
echo "  ThreatSense 2.0 - Development Mode"
echo "========================================="
echo ""

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ ! -d "apps/api" ] || [ ! -d "apps/web" ]; then
    echo -e "${YELLOW}Error: Please run this script from the ThreatSense repo root${NC}"
    exit 1
fi

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}Created .env from .env.example${NC}"
fi

echo -e "${BLUE}Starting Postgres, Redis, Mailpit (if Docker available)...${NC}"
if command -v docker >/dev/null 2>&1; then
    docker compose up -d postgres redis mailpit 2>/dev/null || true
fi

echo -e "${GREEN}[1/3] Installing Python dependencies...${NC}"
cd apps/api
pip install -q -r requirements.txt
alembic upgrade head 2>/dev/null || true
cd ../..

echo -e "${GREEN}[2/3] Installing worker dependencies...${NC}"
cd apps/worker
pip install -q -r requirements.txt
cd ../..

echo -e "${GREEN}[3/3] Installing Node.js dependencies...${NC}"
cd apps/web
npm install --silent
cd ../..

echo ""
echo -e "${BLUE}API Server:${NC}      http://localhost:8000"
echo -e "${BLUE}API Docs:${NC}        http://localhost:8000/docs"
echo -e "${BLUE}Web App:${NC}         http://localhost:3000"
echo -e "${BLUE}Mailpit:${NC}         http://localhost:8025"
echo ""
echo -e "${YELLOW}Demo Login:${NC}"
echo "  Email:    demo@threatsense.com"
echo "  Password: demo123"
echo ""

cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down ThreatSense...${NC}"
    kill $API_PID $WEB_PID $WORKER_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

echo -e "${GREEN}Starting API server...${NC}"
cd apps/api
uvicorn app.main:app --reload --port 8000 > /tmp/threatsense-api.log 2>&1 &
API_PID=$!
cd ../..

echo -e "${GREEN}Starting Celery worker...${NC}"
cd apps/worker
celery -A worker.celery_app worker --loglevel=INFO > /tmp/threatsense-worker.log 2>&1 &
WORKER_PID=$!
cd ../..

sleep 3

echo -e "${GREEN}Starting web app...${NC}"
cd apps/web
npm run dev > /tmp/threatsense-web.log 2>&1 &
WEB_PID=$!
cd ../..

sleep 5

echo ""
echo -e "${GREEN}ThreatSense is running!${NC}"
echo "Press Ctrl+C to stop all services"
echo ""

tail -f /tmp/threatsense-api.log /tmp/threatsense-worker.log /tmp/threatsense-web.log
