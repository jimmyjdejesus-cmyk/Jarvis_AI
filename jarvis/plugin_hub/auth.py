"""Simple authentication and RBAC utilities for the plugin hub."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from uuid import uuid4

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from jarvis.auth.security import security_manager

# In-memory user store for demo purposes
_users: Dict[str, Dict[str, object]] = {
    "admin": {
        "password_hash": security_manager.hash_password("admin"),
        "roles": ["admin"],
    },
    "publisher": {
        "password_hash": security_manager.hash_password("publisher"),
        "roles": ["publisher"],
    },
    "user": {
        "password_hash": security_manager.hash_password("user"),
        "roles": ["user"],
    },
}

# In-memory token store {token: {username, roles, expires}}
_tokens: Dict[str, Dict[str, object]] = {}

bearer_scheme = HTTPBearer(auto_error=False)

TOKEN_EXPIRE_MINUTES = 60


def authenticate_user(username: str, password: str) -> Optional[str]:
    user = _users.get(username)
    if not user:
        return None
    if not security_manager.verify_password(password, user["password_hash"]):
        return None
    token = uuid4().hex
    _tokens[token] = {
        "username": username,
        "roles": user["roles"],
        "expires": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES),
    }
    return token


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> Dict[str, object]:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token_data = _tokens.get(credentials.credentials)
    if not token_data or token_data["expires"] < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return token_data


def require_role(role: Union[str, List[str]]):
    """Dependency that ensures the current user has one of the required roles."""

    roles = [role] if isinstance(role, str) else role

    def _role_dependency(user: Dict[str, object] = Depends(get_current_user)):
        if not any(r in user.get("roles", []) for r in roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
        return user

    return _role_dependency
