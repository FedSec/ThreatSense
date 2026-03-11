from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/admin", tags=["admin"])

class CustomerOnboard(BaseModel):
    company_name: str
    admin_email: EmailStr
    admin_name: str

@router.post("/onboard")
async def onboard_customer(customer: CustomerOnboard):
    """Onboard a new customer - admin only"""
    # TODO: Implement actual customer onboarding logic
    return {
        "message": "Customer onboarding initiated",
        "company": customer.company_name,
        "admin_email": customer.admin_email
    }
