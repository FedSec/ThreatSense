from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.deps import (
    create_access_token,
    get_current_customer,
    get_current_user,
    hash_password,
    verify_password,
)
from app.models import Customer, PlanTier, User
from app.schemas import LoginRequest, RegisterRequest, TokenResponse, UserOut
from app.services.email import send_welcome_email
from app.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/register", response_model=TokenResponse)
async def register(body: RegisterRequest, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.email == body.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    customer = Customer(
        company_name=body.company_name,
        email=body.email,
        plan=PlanTier.STARTER.value,
        notify_email=body.email,
    )
    session.add(customer)
    session.commit()
    session.refresh(customer)

    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
        customer_id=customer.id,
        is_admin=True,
    )
    session.add(user)
    session.commit()

    send_welcome_email(body.email, body.full_name, body.company_name)

    token = create_access_token(
        data={"sub": user.email, "customer_id": customer.id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == credentials.email)).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User inactive")

    token = create_access_token(
        data={"sub": user.email, "customer_id": user.customer_id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserOut)
async def me(
    user: User = Depends(get_current_user),
    customer: Customer = Depends(get_current_customer),
):
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        customer_id=user.customer_id,
        is_admin=user.is_admin,
        plan=customer.plan,
        company_name=customer.company_name,
    )
