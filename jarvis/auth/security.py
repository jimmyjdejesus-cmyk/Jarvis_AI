"""
Security Manager - Authentication and security features
"""

import bcrypt
import logging
import hashlib
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path


try:
    from agent.features.security import *
    LEGACY_SECURITY_AVAILABLE = True
except ImportError:
    LEGACY_SECURITY_AVAILABLE = False

logger = logging.getLogger(__name__)

class SecurityManager:
    """Modern security manager with clean interface"""
    
    def __init__(self):
        self.rate_limit_cache = {}
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        if LEGACY_SECURITY_AVAILABLE:
            try:
                return hash_password(password)
            except:
                pass
        
        # Fallback implementation
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        if LEGACY_SECURITY_AVAILABLE:
            try:
                return verify_password(password, hashed)
            except:
                pass
        
        # Fallback implementation
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except:
            return False
    
    def is_rate_limited(self, identifier: str, max_attempts: int = 5, window_minutes: int = 15) -> bool:
        """Check if identifier is rate limited"""
        if LEGACY_SECURITY_AVAILABLE:
            try:
                return is_rate_limited(identifier, max_attempts, window_minutes)
            except:
                pass
        
        # Fallback implementation
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)
        
        if identifier in self.rate_limit_cache:
            attempts = self.rate_limit_cache[identifier]
            # Remove old attempts
            attempts = [attempt for attempt in attempts if attempt > window_start]
            self.rate_limit_cache[identifier] = attempts
            
            if len(attempts) >= max_attempts:
                return True
        
        return False
    
    def record_attempt(self, identifier: str):
        """Record an attempt for rate limiting"""
        now = datetime.now()
        if identifier not in self.rate_limit_cache:
            self.rate_limit_cache[identifier] = []
        self.rate_limit_cache[identifier].append(now)
    
    def validate_password_strength(self, password: str) -> bool:
        """Validate password strength"""
        if LEGACY_SECURITY_AVAILABLE:
            try:
                return validate_password_strength(password)
            except:
                pass
        
        # Fallback implementation
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        return has_upper and has_lower and has_digit
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate a secure random token"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def log_security_event(self, event_type: str, username: str = None, details: str = None):
        """Log security event"""
        if LEGACY_SECURITY_AVAILABLE:
            try:
                log_security_event(event_type, username, details)
                return
            except:
                pass
        
        # Fallback implementation
        logger.info(f"Security Event: {event_type} - User: {username} - Details: {details}")

# Create global instance
security_manager = SecurityManager()
