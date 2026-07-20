from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from app.config import get_settings
from app.database import get_session
from app.deps import get_current_customer
from app.models import Customer, PlanTier
from app.schemas import CheckoutRequest, CustomerOut
from app.services.billing import create_checkout_session, get_stripe

router = APIRouter(prefix="/billing", tags=["billing"])
settings = get_settings()


@router.get("/plans")
async def list_plans():
    return {
        "plans": [
            {"id": "starter", "name": "Starter", "price_monthly": 99},
            {"id": "professional", "name": "Professional", "price_monthly": 299},
            {"id": "enterprise", "name": "Enterprise", "price_monthly": 599},
        ]
    }


@router.post("/checkout")
async def checkout(
    body: CheckoutRequest,
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    plan = body.plan.lower()
    if plan not in {p.value for p in PlanTier}:
        raise HTTPException(status_code=400, detail="Invalid plan")

    result = create_checkout_session(
        customer_email=customer.email,
        stripe_customer_id=customer.stripe_customer_id,
        plan=plan,
        success_url=f"{settings.FRONTEND_URL}/billing?success=1",
        cancel_url=f"{settings.FRONTEND_URL}/billing?canceled=1",
        client_reference_id=customer.id,
    )

    # Dev mode without Stripe keys: upgrade immediately
    if result.get("dev_mode"):
        customer.plan = plan
        customer.updated_at = datetime.utcnow()
        session.add(customer)
        session.commit()

    return result


@router.post("/webhook")
async def stripe_webhook(request: Request, session: Session = Depends(get_session)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")

    if not settings.STRIPE_WEBHOOK_SECRET or not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Stripe webhook not configured")

    stripe = get_stripe()
    try:
        event = stripe.Webhook.construct_event(
            payload, sig, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if event["type"] == "checkout.session.completed":
        data = event["data"]["object"]
        customer_id = data.get("client_reference_id") or data.get("metadata", {}).get(
            "customer_id"
        )
        plan = data.get("metadata", {}).get("plan", PlanTier.PROFESSIONAL.value)
        stripe_customer = data.get("customer")
        subscription = data.get("subscription")

        if customer_id:
            cust = session.get(Customer, customer_id)
            if cust:
                cust.plan = plan
                cust.stripe_customer_id = stripe_customer
                cust.stripe_subscription_id = subscription
                cust.updated_at = datetime.utcnow()
                session.add(cust)
                session.commit()

    elif event["type"] in ("customer.subscription.deleted", "customer.subscription.updated"):
        data = event["data"]["object"]
        sub_id = data.get("id")
        status = data.get("status")
        cust = session.exec(
            select(Customer).where(Customer.stripe_subscription_id == sub_id)
        ).first()
        if cust and status in ("canceled", "unpaid", "incomplete_expired"):
            cust.plan = PlanTier.STARTER.value
            cust.updated_at = datetime.utcnow()
            session.add(cust)
            session.commit()

    return {"received": True}


@router.post("/dev-upgrade", response_model=CustomerOut)
async def dev_upgrade(
    body: CheckoutRequest,
    customer: Customer = Depends(get_current_customer),
    session: Session = Depends(get_session),
):
    """Local/dev helper when Stripe price IDs are not set."""
    plan = body.plan.lower()
    if plan not in {p.value for p in PlanTier}:
        raise HTTPException(status_code=400, detail="Invalid plan")
    customer.plan = plan
    customer.updated_at = datetime.utcnow()
    session.add(customer)
    session.commit()
    session.refresh(customer)
    from app.routers.customers import customer_to_out

    return customer_to_out(customer)
