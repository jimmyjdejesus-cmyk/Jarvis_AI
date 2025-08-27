from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from config.config_loader import load_config

config = load_config()
auth_cfg = config.get("auth", {})
SECRET_KEY = auth_cfg.get("secret_key", "CHANGE_ME")
ALGORITHM = auth_cfg.get("algorithm", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = auth_cfg.get("access_token_expire_minutes", 30)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Demo users; replace with persistent storage in production
fake_users_db: Dict[str, Dict[str, Any]] = {
    "alice": {
        "username": "alice",
        "hashed_password": bcrypt.hashpw(
            b"secret", bcrypt.gensalt()
        ).decode(),
        "roles": ["admin"],
    },
    "bob": {
        "username": "bob",
        "hashed_password": bcrypt.hashpw(
            b"secret", bcrypt.gensalt()
        ).decode(),
        "roles": ["user"],
    },
}

  

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

  

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user by username and password."""
    user = fake_users_db.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return user

  

def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

  

def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Retrieve the current user from a JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        roles: List[str] = payload.get("roles", [])
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception
    return {"username": username, "roles": roles}

  

def role_required(required_role: str):
    """Dependency enforcing that the current user has a specific role."""

    def dependency(user: Dict[str, Any] = Depends(get_current_user)) -> None:
        if required_role not in user.get("roles", []):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

    return dependency
