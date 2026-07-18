from datetime import datetime

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.deps import get_current_customer
from app.models import Customer
from app.schemas import CustomerOut, CustomerUpdate

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/me", response_model=CustomerOut)
async def get_my_customer(customer: Customer = Depends(get_current_customer)):
    return CustomerOut(
        id=customer.id,
        company_name=customer.company_name,
        email=customer.email,
        plan=customer.plan,
        notify_email=customer.notify_email,
        slack_webhook_url=customer.slack_webhook_url,
        discord_webhook_url=customer.discord_webhook_url,
        stripe_customer_id=customer.stripe_customer_id,
        stripe_subscription_id=customer.stripe_subscription_id,
    )


@router.patch("/me", response_model=CustomerOut)
async def update_my_customer(
    body: CustomerUpdate,
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    if body.notify_email is not None:
        customer.notify_email = body.notify_email
    if body.slack_webhook_url is not None:
        customer.slack_webhook_url = body.slack_webhook_url or None
    if body.discord_webhook_url is not None:
        customer.discord_webhook_url = body.discord_webhook_url or None
    if body.company_name is not None:
        customer.company_name = body.company_name
    customer.updated_at = datetime.utcnow()
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return await get_my_customer(customer)
