"""
Security Manager - Modern authentication and security
"""

import bcrypt
import hashlib
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
import threading

logger = logging.getLogger(__name__)

class SecurityManager:
    """Modern security manager with authentication and rate limiting"""
    
    def __init__(self, database_manager=None):
        self.db_manager = database_manager
        self._rate_limits = {}
        self._failed_attempts = {}
        self._lock = threading.Lock()
        self._path_permissions: Dict[str, List[str]] = {}
        self._command_permissions: Dict[str, List[str]] = {}
        self._role_permissions: Dict[str, Dict[str, List[str]]] = {}
        
        # Rate limiting settings
        self.max_attempts = 5
        self.lockout_duration = 300  # 5 minutes
        self.rate_limit_window = 60  # 1 minute
        self.max_requests_per_window = 10
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        try:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            # Fallback to sha256 if bcrypt fails
            return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            if hashed.startswith('$2b$'):
                # bcrypt hash
                return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
            else:
                # Assume sha256 hash (legacy)
                return hashlib.sha256(password.encode()).hexdigest() == hashed
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def is_rate_limited(self, identifier: str) -> bool:
        """Check if identifier is rate limited"""
        with self._lock:
            current_time = time.time()
            
            # Clean old entries
            self._clean_old_entries(current_time)
            
            # Check failed attempts lockout
            if identifier in self._failed_attempts:
                attempts, last_attempt = self._failed_attempts[identifier]
                if attempts >= self.max_attempts:
                    if current_time - last_attempt < self.lockout_duration:
                        return True
                    else:
                        # Lockout expired, reset
                        del self._failed_attempts[identifier]
            
            # Check rate limiting
            if identifier in self._rate_limits:
                requests = self._rate_limits[identifier]
                # Count requests in current window
                recent_requests = [req_time for req_time in requests 
                                 if current_time - req_time < self.rate_limit_window]
                
                if len(recent_requests) >= self.max_requests_per_window:
                    return True
                
                # Update with recent requests only
                self._rate_limits[identifier] = recent_requests
            
            return False
    
    def record_request(self, identifier: str):
        """Record a request for rate limiting"""
        with self._lock:
            current_time = time.time()
            
            if identifier not in self._rate_limits:
                self._rate_limits[identifier] = []
            
            self._rate_limits[identifier].append(current_time)
    
    def record_failed_attempt(self, identifier: str):
        """Record a failed authentication attempt"""
        with self._lock:
            current_time = time.time()
            
            if identifier in self._failed_attempts:
                attempts, _ = self._failed_attempts[identifier]
                self._failed_attempts[identifier] = (attempts + 1, current_time)
            else:
                self._failed_attempts[identifier] = (1, current_time)
    
    def record_successful_login(self, identifier: str):
        """Record successful login (clears failed attempts)"""
        with self._lock:
            if identifier in self._failed_attempts:
                del self._failed_attempts[identifier]
    
    def _clean_old_entries(self, current_time: float):
        """Clean old rate limiting entries"""
        # Clean rate limits
        for identifier in list(self._rate_limits.keys()):
            requests = self._rate_limits[identifier]
            recent_requests = [req_time for req_time in requests
                             if current_time - req_time < self.rate_limit_window]
            if recent_requests:
                self._rate_limits[identifier] = recent_requests
            else:
                del self._rate_limits[identifier]
        
        # Clean old failed attempts
        for identifier in list(self._failed_attempts.keys()):
            attempts, last_attempt = self._failed_attempts[identifier]
            if current_time - last_attempt > self.lockout_duration:
                del self._failed_attempts[identifier]

    # Permission management
    def grant_path_access(self, username: str, path: str):
        """Grant a specific user access to a file path."""
        resolved = str(Path(path).resolve())
        with self._lock:
            self._path_permissions.setdefault(username, []).append(resolved)

    def grant_command_access(self, username: str, command: str):
        """Grant a specific user access to execute a command."""
        with self._lock:
            self._command_permissions.setdefault(username, []).append(command)

    def grant_role_path_access(self, role: str, path: str):
        """Grant a role access to a file path."""
        resolved = str(Path(path).resolve())
        with self._lock:
            perms = self._role_permissions.setdefault(role, {"paths": [], "commands": []})
            perms["paths"].append(resolved)

    def grant_role_command_access(self, role: str, command: str):
        """Grant a role access to execute a command."""
        with self._lock:
            perms = self._role_permissions.setdefault(role, {"paths": [], "commands": []})
            perms["commands"].append(command)

    def _get_user_role(self, username: str) -> str:
        """Retrieve a user's role from the database manager if available."""
        if not self.db_manager:
            return "user"
        try:
            user = self.db_manager.get_user(username)
            if not user:
                return "user"
            return user.get("role", "user")
        except Exception:
            return "user"

    def has_path_access(self, username: str, path: str) -> bool:
        """Check if a user (via role or direct grant) can access a path."""
        resolved_path = Path(path).resolve()
        role = self._get_user_role(username)
        with self._lock:
            user_paths = self._path_permissions.get(username, [])
            role_paths = self._role_permissions.get(role, {}).get("paths", [])
        allowed_paths = user_paths + role_paths
        return any(resolved_path.is_relative_to(Path(p)) for p in allowed_paths)

    def has_command_access(self, username: str, command: str) -> bool:
        """Check if a user (via role or direct grant) can run a command."""
        role = self._get_user_role(username)
        base_command = command.strip().split()[0] if command.strip() else ""
        with self._lock:
            user_cmds = self._command_permissions.get(username, [])
            role_cmds = self._role_permissions.get(role, {}).get("commands", [])
        return base_command in user_cmds or base_command in role_cmds
    
    def authenticate_user(self, username: str, password: str, 
                         ip_address: str = None) -> Optional[Dict]:
        """Authenticate user with rate limiting and logging"""
        identifier = ip_address or username
        
        # Check rate limiting
        if self.is_rate_limited(identifier):
            if self.db_manager:
                self.db_manager.log_security_event(
                    username, "RATE_LIMITED", 
                    f"Authentication blocked due to rate limiting",
                    ip_address, False
                )
            logger.warning(f"Rate limited authentication attempt for {username}")
            return None
        
        # Record the request
        self.record_request(identifier)
        
        try:
            # Get user from database
            if not self.db_manager:
                logger.error("No database manager available for authentication")
                return None
            
            user = self.db_manager.get_user(username)
            if not user:
                self.record_failed_attempt(identifier)
                if self.db_manager:
                    self.db_manager.log_security_event(
                        username, "LOGIN_FAILED", 
                        "User not found", ip_address, False
                    )
                return None
            
            # Check if user is active
            if not user.get('is_active', True):
                self.record_failed_attempt(identifier)
                if self.db_manager:
                    self.db_manager.log_security_event(
                        username, "LOGIN_FAILED", 
                        "Account disabled", ip_address, False
                    )
                return None
            
            # Verify password
            if not self.verify_password(password, user['password_hash']):
                self.record_failed_attempt(identifier)
                if self.db_manager:
                    self.db_manager.log_security_event(
                        username, "LOGIN_FAILED", 
                        "Invalid password", ip_address, False
                    )
                return None
            
            # Authentication successful
            self.record_successful_login(identifier)
            
            # Update last login
            self.db_manager.update_last_login(username)
            
            # Log successful login
            if self.db_manager:
                self.db_manager.log_security_event(
                    username, "LOGIN_SUCCESS", 
                    "Successful authentication", ip_address, True
                )
            
            logger.info(f"Successful authentication for user: {username}")
            
            # Return user info (without password hash)
            user_info = user.copy()
            user_info.pop('password_hash', None)
            return user_info
            
        except Exception as e:
            logger.error(f"Authentication error for {username}: {e}")
            self.record_failed_attempt(identifier)
            if self.db_manager:
                self.db_manager.log_security_event(
                    username, "LOGIN_ERROR", 
                    f"Authentication error: {str(e)}", ip_address, False
                )
            return None
    
    def create_user(self, username: str, password: str, email: str = None, 
                   role: str = 'user') -> bool:
        """Create new user with hashed password"""
        try:
            if not self.db_manager:
                logger.error("No database manager available for user creation")
                return False
            
            # Hash the password
            password_hash = self.hash_password(password)
            
            # Create user in database
            success = self.db_manager.create_user(username, password_hash, email, role)
            
            if success and self.db_manager:
                self.db_manager.log_security_event(
                    username, "USER_CREATED", 
                    f"New user created with role: {role}", None, True
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Error creating user {username}: {e}")
            return False
    
    def get_security_info(self) -> Dict:
        """Get current security status"""
        with self._lock:
            return {
                'active_rate_limits': len(self._rate_limits),
                'failed_attempts': len(self._failed_attempts),
                'max_attempts': self.max_attempts,
                'lockout_duration': self.lockout_duration,
                'rate_limit_window': self.rate_limit_window,
                'max_requests_per_window': self.max_requests_per_window
            }

# Global instance
_security_manager = None

def get_security_manager(database_manager=None) -> SecurityManager:
    """Get global security manager instance"""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager(database_manager)
    return _security_manager
