from sqlmodel import create_engine, SQLModel, Session
from typing import Generator
import os

# Database URL - use PostgreSQL in production, SQLite for development
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://threatsense:threatsense_password@localhost:5432/threatsense"
)

# For local development, you can use SQLite:
# DATABASE_URL = "sqlite:///./threatsense.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)


def create_db_and_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency for getting database sessions"""
    with Session(engine) as session:
        yield session


def init_db():
    """Initialize database with sample data"""
    from app.models import Customer, User
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    create_db_and_tables()

    with Session(engine) as session:
        # Check if demo customer already exists
        from sqlmodel import select
        statement = select(Customer).where(Customer.email == "demo@threatsense.com")
        existing = session.exec(statement).first()

        if not existing:
            # Create demo customer
            demo_customer = Customer(
                company_name="Demo Company",
                email="demo@threatsense.com"
            )
            session.add(demo_customer)
            session.commit()
            session.refresh(demo_customer)

            # Create demo user
            demo_user = User(
                email="demo@threatsense.com",
                hashed_password=pwd_context.hash("demo123"),
                full_name="Demo User",
                customer_id=demo_customer.id,
                is_admin=True
            )
            session.add(demo_user)
            session.commit()

            print("✅ Demo account created: demo@threatsense.com / demo123")
        else:
            print("✅ Demo account already exists")
