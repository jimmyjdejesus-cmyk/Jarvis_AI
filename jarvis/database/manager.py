"""
Database Manager - Modern interface for all database operations
"""

import sqlite3
import json
import logging
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from pathlib import Path

# Legacy imports will be loaded dynamically when needed
LEGACY_DB_AVAILABLE = False

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Modern database manager with clean interface"""
    
    def __init__(self, db_path: str = "janus_database.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self.init_database()
    
    def init_database(self):
        """Initialize database with all required tables"""
        if LEGACY_DB_AVAILABLE:
            # Use legacy initialization if available
            try:
                init_db()
                return
            except Exception as e:
                logger.warning(f"Legacy init failed: {e}")
        
        # Fallback initialization
        with self._lock:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    is_active BOOLEAN DEFAULT 1,
                    is_verified BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME,
                    failed_login_attempts INTEGER DEFAULT 0,
                    locked_until DATETIME
                )
            ''')
            
            # User preferences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    preference_key TEXT NOT NULL,
                    preference_value TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(username, preference_key),
                    FOREIGN KEY (username) REFERENCES users (username)
                )
            ''')
            
            # Security logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS security_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    username TEXT,
                    ip_address TEXT,
                    details TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        if LEGACY_DB_AVAILABLE:
            try:
                return get_user(username)
            except Exception:
                pass

        # Fallback implementation
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, name, email, hashed_password, role, is_active, is_verified FROM users WHERE username = ?",
                (username,)
            )
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    "id": result[0],
                    "username": result[1],
                    "name": result[2],
                    "email": result[3],
                    "hashed_password": result[4],
                    "role": result[5],
                    "is_active": bool(result[6]),
                    "is_verified": bool(result[7])
                }
        return None
    
    def create_user(self, username: str, name: str, email: str, hashed_password: str, role: str = "user") -> bool:
        """Create a new user"""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (username, name, email, hashed_password, role, is_active, is_verified)
                    VALUES (?, ?, ?, ?, ?, 1, 1)
                ''', (username, name, email, hashed_password, role))
                conn.commit()
                conn.close()
                return True
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            return False
    
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        if LEGACY_DB_AVAILABLE:
            try:
                return get_all_users()
            except:
                pass
        
        # Fallback implementation
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT username, name, role, is_active FROM users")
            results = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "username": row[0],
                    "name": row[1],
                    "role": row[2],
                    "is_active": bool(row[3])
                }
                for row in results
            ]
    
    def log_security_event(self, event_type: str, username: str = None, details: str = None):
        """Log security event"""
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO security_logs (event_type, username, details) VALUES (?, ?, ?)",
                    (event_type, username, details)
                )
                conn.commit()
                conn.close()
        except Exception as e:
            logger.error(f"Failed to log security event: {e}")
    
    def get_user_preferences(self, username: str) -> Dict:
        """Get user preferences"""
        if LEGACY_DB_AVAILABLE:
            try:
                return get_user_preferences(username)
            except Exception:
                pass

        # Fallback implementation
        prefs = {}
        try:
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT preference_key, preference_value FROM user_preferences WHERE username = ?",
                    (username,)
                )
                results = cursor.fetchall()
                conn.close()
                
                for key, value in results:
                    try:
                        prefs[key] = json.loads(value)
                    except:
                        prefs[key] = value
        except Exception as e:
            logger.error(f"Failed to get user preferences: {e}")
        
        return prefs
    
    def save_user_preference(self, username: str, key: str, value: Any):
        """Save user preference"""
        if LEGACY_DB_AVAILABLE:
            try:
                return save_user_preference(username, key, value)
            except:
                pass
        
        # Fallback implementation
        try:
            value_json = json.dumps(value)
            with self._lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO user_preferences (username, preference_key, preference_value, updated_at)
                    VALUES (?, ?, ?, ?)
                ''', (username, key, value_json, datetime.now().isoformat()))
                conn.commit()
                conn.close()
        except Exception as e:
            logger.error(f"Failed to save user preference: {e}")

# Create global instance
db_manager = DatabaseManager()
