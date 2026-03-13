from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from typing import Optional

router = APIRouter(prefix="/auth", tags=["auth"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings - In production, use environment variables
SECRET_KEY = "your-secret-key-change-in-production"  # CHANGE THIS
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Mock user database - Replace with real database in production
# Pre-hashed password for demo123
MOCK_USERS = {
    "demo@threatsense.com": {
        "email": "demo@threatsense.com",
        "hashed_password": "$2b$12$mWJqgooZJStSokhOTHQvPOg7QV6AF73wRwvA6.nAJ4soh7h7ZGUpW",  # Password: demo123
        "full_name": "Demo User",
        "customer_id": "customer_001"
    }
}

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest):
    """
    Login endpoint - authenticates user and returns JWT token
    Default credentials: demo@threatsense.com / demo123
    """
    user = MOCK_USERS.get(credentials.email)

    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": credentials.email, "customer_id": user["customer_id"]},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def get_current_user():
    """Get current user info - requires authentication"""
    # TODO: Implement JWT token verification
    return {"email": "demo@threatsense.com", "full_name": "Demo User"}
