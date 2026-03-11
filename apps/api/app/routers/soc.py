from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/soc", tags=["soc"])

class SOCAlert(BaseModel):
    id: str
    severity: str
    title: str
    description: str

@router.get("/alerts", response_model=List[SOCAlert])
async def get_soc_alerts():
    """Get SOC alerts - placeholder for SOCaaS functionality"""
    return []

@router.get("/dashboard")
async def get_soc_dashboard():
    """Get SOC dashboard metrics"""
    return {
        "total_alerts": 0,
        "critical_alerts": 0,
        "open_incidents": 0,
        "mean_time_to_respond": "0m"
    }
