from typing import Optional

import stripe
from fastapi import HTTPException

from app.config import get_settings
from app.models import PlanTier

settings = get_settings()

PLAN_PRICES = {
    PlanTier.STARTER.value: lambda: settings.STRIPE_PRICE_STARTER,
    PlanTier.PROFESSIONAL.value: lambda: settings.STRIPE_PRICE_PROFESSIONAL,
    PlanTier.ENTERPRISE.value: lambda: settings.STRIPE_PRICE_ENTERPRISE,
}

# Plugins allowed per plan
PLAN_PLUGINS = {
    PlanTier.STARTER.value: {"nuclei_scan"},
    PlanTier.PROFESSIONAL.value: {"nuclei_scan", "nmap_stub", "soc_rules"},
    PlanTier.ENTERPRISE.value: {"nuclei_scan", "nmap_stub", "soc_rules"},
}


def assert_plugin_allowed(plan: str, plugin: str) -> None:
    allowed = PLAN_PLUGINS.get(plan or PlanTier.STARTER.value, PLAN_PLUGINS[PlanTier.STARTER.value])
    if plugin not in allowed:
        raise HTTPException(
            status_code=403,
            detail=f"Plugin '{plugin}' requires a higher plan. Current plan: {plan}",
        )


def get_stripe() -> stripe:
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=503,
            detail="Stripe is not configured. Set STRIPE_SECRET_KEY.",
        )
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


def price_id_for_plan(plan: str) -> str:
    if plan not in PLAN_PRICES:
        raise HTTPException(status_code=400, detail=f"Unknown plan: {plan}")
    price_id = PLAN_PRICES[plan]()
    if not price_id:
        # Dev fallback: allow plan upgrade without Stripe when prices unset
        return ""
    return price_id


def create_checkout_session(
    *,
    customer_email: str,
    stripe_customer_id: Optional[str],
    plan: str,
    success_url: str,
    cancel_url: str,
    client_reference_id: str,
) -> dict:
    price_id = price_id_for_plan(plan)
    if not price_id:
        return {
            "id": "dev_checkout",
            "url": f"{settings.FRONTEND_URL}/billing?dev_upgrade={plan}",
            "dev_mode": True,
            "plan": plan,
        }

    s = get_stripe()
    params = {
        "mode": "subscription",
        "success_url": success_url,
        "cancel_url": cancel_url,
        "line_items": [{"price": price_id, "quantity": 1}],
        "client_reference_id": client_reference_id,
        "metadata": {"plan": plan, "customer_id": client_reference_id},
    }
    if stripe_customer_id:
        params["customer"] = stripe_customer_id
    else:
        params["customer_email"] = customer_email

    session = s.checkout.Session.create(**params)
    return {"id": session.id, "url": session.url, "dev_mode": False, "plan": plan}
