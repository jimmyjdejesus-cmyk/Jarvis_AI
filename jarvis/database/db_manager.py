"""
Database Manager - Modern interface for all database operations
"""

import sqlite3
import json
import logging
import threading
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Modern database manager with clean interface"""
    
    def __init__(self, db_path: str = "jarvis_modern.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialize database with required tables"""
        with self._lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE,
                        password_hash TEXT NOT NULL,
                        role TEXT DEFAULT 'user',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1,
                        preferences TEXT DEFAULT '{}'
                    )
                ''')
                
                # Security events table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS security_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        event_type TEXT NOT NULL,
                        details TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ip_address TEXT,
                        success BOOLEAN DEFAULT 1
                    )
                ''')
                
                # User preferences table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        preference_key TEXT NOT NULL,
                        preference_value TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(username, preference_key)
                    )
                ''')
                
                # Chat history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS chat_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        message TEXT NOT NULL,
                        response TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        model_used TEXT,
                        session_id TEXT
                    )
                ''')
                
                conn.commit()
                conn.close()
                logger.info("Database initialized successfully")
                
            except Exception as e:
                logger.error(f"Database initialization failed: {e}")
                raise
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        with self._lock:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, username, email, password_hash, role, 
                           created_at, last_login, is_active, preferences
                    FROM users WHERE username = ?
                ''', (username,))
                
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    return {
                        'id': row[0],
                        'username': row[1],
                        'email': row[2],
                        'password_hash': row[3],
                        'role': row[4],
                        'created_at': row[5],
                        'last_login': row[6],
                        'is_active': bool(row[7]),
                        'preferences': json.loads(row[8] or '{}')
                    }
                return None
                
            except Exception as e:
                logger.error(f"Error getting user {username}: {e}")
                return None
    
    def create_user(self, username: str, password_hash: str, email: str = None, 
                   role: str = 'user') -> bool:
        """Create new user"""
        with self._lock:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, role, preferences)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, email, password_hash, role, '{}'))
                
                conn.commit()
                conn.close()
                
                logger.info(f"User {username} created successfully")
                return True
                
            except sqlite3.IntegrityError:
                logger.warning(f"User {username} already exists")
                return False
            except Exception as e:
                logger.error(f"Error creating user {username}: {e}")
                return False
    
    def update_last_login(self, username: str) -> bool:
        """Update user's last login timestamp"""
        with self._lock:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE users SET last_login = CURRENT_TIMESTAMP
                    WHERE username = ?
                ''', (username,))
                
                conn.commit()
                conn.close()
                return True
                
            except Exception as e:
                logger.error(f"Error updating last login for {username}: {e}")
                return False
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        with self._lock:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, username, email, role, created_at, 
                           last_login, is_active
                    FROM users ORDER BY created_at DESC
                ''')
                
                rows = cursor.fetchall()
                conn.close()
                
                return [{
                    'id': row[0],
                    'username': row[1],
                    'email': row[2],
                    'role': row[3],
                    'created_at': row[4],
                    'last_login': row[5],
                    'is_active': bool(row[6])
                } for row in rows]
                
            except Exception as e:
                logger.error(f"Error getting all users: {e}")
                return []
    
    def log_security_event(self, username: str, event_type: str, 
                          details: str = None, ip_address: str = None, 
                          success: bool = True) -> bool:
        """Log security event"""
        with self._lock:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO security_events 
                    (username, event_type, details, ip_address, success)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, event_type, details, ip_address, success))
                
                conn.commit()
                conn.close()
                return True
                
            except Exception as e:
                logger.error(f"Error logging security event: {e}")
                return False
    
    def get_user_preferences(self, username: str) -> Dict[str, Any]:
        """Get user preferences"""
        with self._lock:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT preference_key, preference_value 
                    FROM user_preferences WHERE username = ?
                ''', (username,))
                
                rows = cursor.fetchall()
                conn.close()
                
                preferences = {}
                for row in rows:
                    try:
                        preferences[row[0]] = json.loads(row[1])
                    except:
                        preferences[row[0]] = row[1]
                
                return preferences
                
            except Exception as e:
                logger.error(f"Error getting preferences for {username}: {e}")
                return {}
    
    def save_user_preference(self, username: str, key: str, value: Any) -> bool:
        """Save user preference"""
        with self._lock:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                value_json = json.dumps(value)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO user_preferences 
                    (username, preference_key, preference_value, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (username, key, value_json))
                
                conn.commit()
                conn.close()
                return True
                
            except Exception as e:
                logger.error(f"Error saving preference for {username}: {e}")
                return False
    
    def save_chat_message(self, username: str, message: str, response: str = None,
                         model_used: str = None, session_id: str = None) -> bool:
        """Save chat message and response"""
        with self._lock:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO chat_history 
                    (username, message, response, model_used, session_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, message, response, model_used, session_id))
                
                conn.commit()
                conn.close()
                return True
                
            except Exception as e:
                logger.error(f"Error saving chat message: {e}")
                return False
    
    def get_chat_history(self, username: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get chat history for user"""
        with self._lock:
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT message, response, timestamp, model_used, session_id
                    FROM chat_history 
                    WHERE username = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (username, limit))
                
                rows = cursor.fetchall()
                conn.close()
                
                return [{
                    'message': row[0],
                    'response': row[1],
                    'timestamp': row[2],
                    'model_used': row[3],
                    'session_id': row[4]
                } for row in rows]
                
            except Exception as e:
                logger.error(f"Error getting chat history for {username}: {e}")
                return []

# Global instance
_db_manager = None

def get_database_manager() -> DatabaseManager:
    """Get global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
