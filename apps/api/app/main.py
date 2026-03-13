from dotenv import load_dotenv
load_dotenv(dotenv_path="/home/bebasset/threatsense/ThreatSense-2.0-main/ThreatSense-main/.env")

from fastapi import FastAPI
from app.routers.health import router as health_router
from app.routers.auth import router as auth_router
from app.routers.assets import router as assets_router
from app.routers.scans import router as scans_router
from app.routers.soc import router as soc_router
from app.routers.findings import router as findings_router
from app.routers.admin_onboarding import router as admin_onboarding_router
from app.routers.invite_claim import router as invite_claim_router
from app.routers.ai import router as ai_router
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    print("🚀 Initializing ThreatSense API...")
    try:
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database initialization failed: {e}")
        print("   Using in-memory fallback mode")
    yield
    print("👋 Shutting down ThreatSense API")


app = FastAPI(
    title="ThreatSense API",
    description="Automated SOCaaS, PTaaS, and Vulnerability Scanning Platform",
    version="2.0.0",
    lifespan=lifespan
)

# CORS: allow your frontend to call this API
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # Replace with your real Vercel domain(s):
    "https://threat-sense-2-0.vercel.app",
    # If you add a custom domain later:
    # "https://yourdomain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(assets_router)
app.include_router(scans_router)
app.include_router(soc_router)
app.include_router(findings_router)
app.include_router(admin_onboarding_router)
app.include_router(invite_claim_router)
app.include_router(ai_router)
