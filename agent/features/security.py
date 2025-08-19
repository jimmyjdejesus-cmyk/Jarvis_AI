import os
import time
import secrets
import logging
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
import bcrypt
import json
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting storage (in production, use Redis or database)
_rate_limit_storage: Dict[str, list] = {}

def load_user_key(key_path):
    """Load or generate encryption key for user data"""
    if os.path.exists(key_path):
        with open(key_path, "rb") as f:
            return f.read()
    key = Fernet.generate_key()
    with open(key_path, "wb") as f:
        f.write(key)
    return key

def encrypt_json(data, key):
    """Encrypt JSON data using Fernet symmetric encryption"""
    f = Fernet(key)
    raw = json.dumps(data).encode()
    return f.encrypt(raw)

def decrypt_json(enc, key):
    """Decrypt JSON data using Fernet symmetric encryption"""
    f = Fernet(key)
    raw = f.decrypt(enc)
    return json.loads(raw)

def hash_password(password: str) -> str:
    """Hash password using bcrypt for secure storage"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False

def generate_reset_token() -> str:
    """Generate secure reset token"""
    return secrets.token_urlsafe(32)

def generate_2fa_secret() -> str:
    """Generate 2FA secret key"""
    return secrets.token_hex(16)

def is_rate_limited(identifier: str, max_attempts: int = 5, window_minutes: int = 15) -> bool:
    """Simple rate limiting based on identifier (IP, username, etc.)"""
    now = time.time()
    window_start = now - (window_minutes * 60)
    
    if identifier not in _rate_limit_storage:
        _rate_limit_storage[identifier] = []
    
    # Clean old attempts
    _rate_limit_storage[identifier] = [
        attempt_time for attempt_time in _rate_limit_storage[identifier] 
        if attempt_time > window_start
    ]
    
    # Check if rate limited
    if len(_rate_limit_storage[identifier]) >= max_attempts:
        return True
    
    # Record this attempt
    _rate_limit_storage[identifier].append(now)
    return False

def log_security_event(event_type: str, username: str = None, ip_address: str = None, details: str = None):
    """Log security events for admin review"""
    event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "username": username,
        "ip_address": ip_address,
        "details": details
    }
    logger.info(f"Security Event: {json.dumps(event)}")

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password meets security requirements"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "Password must contain at least one special character"
    
    return True, "Password meets security requirements"