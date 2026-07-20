from datetime import datetime

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.deps import get_current_customer
from app.models import DEFAULT_TELEGRAM_API_URL, Customer
from app.schemas import CustomerOut, CustomerUpdate
from app.services.telegram import normalize_telegram_api_url

router = APIRouter(prefix="/customers", tags=["customers"])


def customer_to_out(customer: Customer) -> CustomerOut:
    return CustomerOut(
        id=customer.id,
        company_name=customer.company_name,
        email=customer.email,
        plan=customer.plan,
        notify_email=customer.notify_email,
        notify_channel=customer.notify_channel or "email",
        telegram_bot_token=customer.telegram_bot_token,
        telegram_chat_id=customer.telegram_chat_id,
        telegram_api_url=customer.telegram_api_url or DEFAULT_TELEGRAM_API_URL,
        slack_webhook_url=customer.slack_webhook_url,
        discord_webhook_url=customer.discord_webhook_url,
        stripe_customer_id=customer.stripe_customer_id,
        stripe_subscription_id=customer.stripe_subscription_id,
    )


@router.get("/me", response_model=CustomerOut)
async def get_my_customer(customer: Customer = Depends(get_current_customer)):
    return customer_to_out(customer)


@router.patch("/me", response_model=CustomerOut)
async def update_my_customer(
    body: CustomerUpdate,
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    if "notify_email" in body.model_fields_set:
        customer.notify_email = body.notify_email or None
    if body.notify_channel is not None:
        customer.notify_channel = body.notify_channel
    if "telegram_bot_token" in body.model_fields_set:
        customer.telegram_bot_token = body.telegram_bot_token or None
    if "telegram_chat_id" in body.model_fields_set:
        customer.telegram_chat_id = body.telegram_chat_id or None
    if "telegram_api_url" in body.model_fields_set:
        customer.telegram_api_url = (
            normalize_telegram_api_url(body.telegram_api_url)
            if body.telegram_api_url
            else DEFAULT_TELEGRAM_API_URL
        )
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
    return customer_to_out(customer)
