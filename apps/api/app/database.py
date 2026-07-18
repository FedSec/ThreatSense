from sqlmodel import create_engine, SQLModel, Session
from typing import Generator
from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def init_db():
    """Create tables and seed demo account."""
    from app.models import Customer, User, PlanTier
    from passlib.context import CryptContext
    from sqlmodel import select

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    create_db_and_tables()

    with Session(engine) as session:
        existing = session.exec(
            select(Customer).where(Customer.email == "demo@threatsense.com")
        ).first()

        if not existing:
            demo_customer = Customer(
                company_name="Demo Company",
                email="demo@threatsense.com",
                plan=PlanTier.ENTERPRISE.value,
                notify_email="demo@threatsense.com",
            )
            session.add(demo_customer)
            session.commit()
            session.refresh(demo_customer)

            demo_user = User(
                email="demo@threatsense.com",
                hashed_password=pwd_context.hash("demo123"),
                full_name="Demo User",
                customer_id=demo_customer.id,
                is_admin=True,
            )
            session.add(demo_user)
            session.commit()
            print("Demo account created: demo@threatsense.com / demo123")
        else:
            print("Demo account already exists")
