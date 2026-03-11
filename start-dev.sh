#!/bin/bash

# ThreatSense Development Startup Script

echo "========================================="
echo "  ThreatSense 2.0 - Development Mode"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "apps/api" ] || [ ! -d "apps/web" ]; then
    echo -e "${YELLOW}Error: Please run this script from the ThreatSense-main directory${NC}"
    exit 1
fi

echo -e "${BLUE}Installing dependencies...${NC}"
echo ""

# Install backend dependencies
echo -e "${GREEN}[1/2] Installing Python dependencies...${NC}"
cd apps/api
pip install -q -r requirements.txt
cd ../..

# Install frontend dependencies
echo -e "${GREEN}[2/2] Installing Node.js dependencies...${NC}"
cd apps/web
npm install --silent
cd ../..

echo ""
echo -e "${GREEN}Dependencies installed successfully!${NC}"
echo ""
echo "========================================="
echo "  Starting Services"
echo "========================================="
echo ""
echo -e "${BLUE}API Server:${NC}      http://localhost:8000"
echo -e "${BLUE}API Docs:${NC}        http://localhost:8000/docs"
echo -e "${BLUE}Web App:${NC}         http://localhost:3000"
echo ""
echo -e "${YELLOW}Demo Login:${NC}"
echo "  Email:    demo@threatsense.com"
echo "  Password: demo123"
echo ""
echo "========================================="
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down ThreatSense...${NC}"
    kill $API_PID $WEB_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start API server in background
echo -e "${GREEN}Starting API server...${NC}"
cd apps/api
uvicorn app.main:app --reload --port 8000 > /tmp/threatsense-api.log 2>&1 &
API_PID=$!
cd ../..

# Wait a moment for API to start
sleep 3

# Start web server in background
echo -e "${GREEN}Starting web app...${NC}"
cd apps/web
npm run dev > /tmp/threatsense-web.log 2>&1 &
WEB_PID=$!
cd ../..

# Wait a moment for web to start
sleep 5

echo ""
echo -e "${GREEN}✓ ThreatSense is running!${NC}"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Keep script running and show logs
tail -f /tmp/threatsense-api.log /tmp/threatsense-web.log
