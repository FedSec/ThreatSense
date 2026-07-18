from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers.health import router as health_router
from app.routers.auth import router as auth_router
from app.routers.assets import router as assets_router
from app.routers.scans import router as scans_router
from app.routers.soc import router as soc_router
from app.routers.findings import router as findings_router
from app.routers.admin_onboarding import router as admin_onboarding_router
from app.routers.invite_claim import router as invite_claim_router
from app.routers.ai import router as ai_router
from app.routers.customers import router as customers_router
from app.routers.billing import router as billing_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing ThreatSense API...")
    try:
        init_db()
        print("Database initialized")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        print("Ensure PostgreSQL is running and DATABASE_URL is correct")
    yield
    print("Shutting down ThreatSense API")


app = FastAPI(
    title="ThreatSense API",
    description="Automated SOCaaS, PTaaS, and Vulnerability Scanning Platform",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
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
app.include_router(customers_router)
app.include_router(billing_router)
app.include_router(admin_onboarding_router)
app.include_router(invite_claim_router)
app.include_router(ai_router)
