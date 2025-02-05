"""Authentication and authorization for the collector service."""

from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
import bcrypt
from pydantic import BaseModel
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Security settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    logger.warning("JWT_SECRET_KEY not set! Generating a random key...")
    SECRET_KEY = os.urandom(32).hex()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
MAX_FAILED_LOGIN_ATTEMPTS = int(os.getenv("MAX_FAILED_LOGIN_ATTEMPTS", "5"))
LOCKOUT_DURATION_MINUTES = int(os.getenv("LOCKOUT_DURATION_MINUTES", "15"))

class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Token data model."""
    username: Optional[str] = None
    scopes: list[str] = []

class User(BaseModel):
    """User model."""
    username: str
    disabled: Optional[bool] = None
    scopes: list[str] = []

class UserInDB(User):
    """User model with hashed password."""
    hashed_password: str

# Password hashing context
def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Mock user database - replace with real database in production
fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": get_password_hash("admin"),  # Change in production
        "disabled": False,
        "scopes": ["logs:write", "logs:read", "admin"]
    }
}



def get_user(db: Dict, username: str) -> Optional[UserInDB]:
    """Get user from database."""
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(db: Dict, username: str, password: str) -> Optional[User]:
    """Authenticate a user."""
    if username not in db:
        return None
    user_dict = db[username]
    if not verify_password(password, user_dict["hashed_password"]):
        return None
    return User(**user_dict)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from JWT token with enhanced security checks."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode and verify the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Basic token validation
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
        # Validate token expiration
        exp = payload.get("exp")
        if not exp or datetime.fromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # IP validation (if token was issued with IP binding)
        token_ip = payload.get("ip")
        if token_ip and token_ip != request.client.host:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token was issued for a different IP address",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Get user and validate scopes
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(username=username, scopes=token_scopes)
        
    except JWTError as e:
        logger.warning(f"JWT validation failed: {str(e)}")
        raise credentials_exception
        
    # Get and validate user
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        logger.warning(f"User not found: {username}")
        raise credentials_exception
        
    # Update user scopes from token
    user.scopes = token_data.scopes
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def check_scope(required_scope: str, user: User = Depends(get_current_active_user)):
    """Check if user has required scope."""
    if required_scope not in user.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not enough permissions. Required scope: {required_scope}"
        )
