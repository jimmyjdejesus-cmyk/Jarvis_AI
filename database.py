import sqlite3
import json
import logging
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

DB_NAME = 'janus_database.db'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection lock to prevent concurrent access issues
_db_lock = threading.Lock()


def init_db():
    """Initializes the database and creates all necessary tables if they don't exist."""
    with _db_lock:
        conn = sqlite3.connect(DB_NAME, timeout=10.0)
        cursor = conn.cursor()

    # Users table with role management
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS users
                   (
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
                       reset_token TEXT,
                       reset_token_expires DATETIME,
                       two_fa_secret TEXT,
                       two_fa_enabled BOOLEAN DEFAULT 0,
                       failed_login_attempts INTEGER DEFAULT 0,
                       locked_until DATETIME
                   )
                   ''')

    # User sessions table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS user_sessions
                   (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       session_id TEXT UNIQUE NOT NULL,
                       username TEXT NOT NULL,
                       created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                       expires_at DATETIME NOT NULL,
                       ip_address TEXT,
                       user_agent TEXT,
                       is_active BOOLEAN DEFAULT 1,
                       FOREIGN KEY (username) REFERENCES users (username)
                   )
                   ''')

    # User preferences table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS user_preferences
                   (
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
                   CREATE TABLE IF NOT EXISTS security_logs
                   (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       event_type TEXT NOT NULL,
                       username TEXT,
                       ip_address TEXT,
                       user_agent TEXT,
                       details TEXT,
                       timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                   )
                   ''')

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS chat_sessions
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       username
                       TEXT
                       NOT
                       NULL,
                       project_name
                       TEXT
                       NOT
                       NULL,
                       session_name
                       TEXT
                       NOT
                       NULL,
                       timestamp
                       DATETIME
                       DEFAULT
                       CURRENT_TIMESTAMP
                   )
                   ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS chat_logs
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       session_id
                       INTEGER
                       NOT
                       NULL,
                       role
                       TEXT
                       NOT
                       NULL,
                       content
                       TEXT
                       NOT
                       NULL,
                       sources
                       TEXT,
                       timestamp
                       DATETIME
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       FOREIGN
                       KEY
                   (
                       session_id
                   ) REFERENCES chat_sessions
                   (
                       id
                   )
                       )
                   ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS pending_users
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       username
                       TEXT
                       UNIQUE
                       NOT
                       NULL,
                       name
                       TEXT
                       NOT
                       NULL,
                       email
                       TEXT
                       NOT
                       NULL,
                       hashed_password
                       TEXT
                       NOT
                       NULL
                   )
                   ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS projects
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       username
                       TEXT
                       NOT
                       NULL,
                       project_name
                       TEXT
                       NOT
                       NULL,
                       UNIQUE
                   (
                       username,
                       project_name
                   )
                       )
                   ''')
    conn.commit()
    conn.close()


def get_projects(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT project_name FROM projects WHERE username = ?", (username,))
    projects = [row[0] for row in cursor.fetchall()]
    if not projects:
        add_project(username, "default")
        projects = ["default"]
    conn.close()
    return projects


def add_project(username, project_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO projects (username, project_name) VALUES (?, ?)", (username, project_name))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()


def create_new_session(username, project_name):
    session_name = f"Session - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_sessions (username, project_name, session_name) VALUES (?, ?, ?)",
        (username, project_name, session_name)
    )
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id


def get_sessions_for_project(username, project_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, session_name FROM chat_sessions WHERE username = ? AND project_name = ? ORDER BY timestamp DESC",
        (username, project_name)
    )
    sessions = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
    conn.close()
    return sessions


def save_message(session_id, role, content, sources=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    sources_json = json.dumps(sources) if sources else None
    cursor.execute(
        "INSERT INTO chat_logs (session_id, role, content, sources) VALUES (?, ?, ?, ?)",
        (session_id, role, content, sources_json)
    )
    conn.commit()
    conn.close()


def load_session_history(session_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content, sources FROM chat_logs WHERE session_id = ? ORDER BY timestamp ASC",
        (session_id,)
    )
    history = []
    for row in cursor.fetchall():
        sources_list = json.loads(row[2]) if row[2] else []
        history.append({"role": row[0], "content": row[1], "sources": sources_list})
    conn.close()
    return history


def add_pending_user(username, name, email, hashed_password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO pending_users (username, name, email, hashed_password) VALUES (?, ?, ?, ?)",
            (username, name, email, hashed_password)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_pending_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username, name, email, hashed_password FROM pending_users")
    users = [{"username": row[0], "name": row[1], "email": row[2], "hashed_password": row[3]} for row in
             cursor.fetchall()]
    conn.close()
    return users


def remove_pending_user(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pending_users WHERE username = ?", (username,))
    conn.commit()
    conn.close()

def rename_session(session_id, new_name):
    """Rename a chat session given its ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE chat_sessions SET session_name = ? WHERE id = ?", (new_name, session_id))
    conn.commit()
    conn.close()


# === USER MANAGEMENT FUNCTIONS ===

def create_user(username: str, name: str, email: str, hashed_password: str, role: str = 'user') -> bool:
    """Create a new user in the database"""
    with _db_lock:
        conn = sqlite3.connect(DB_NAME, timeout=10.0)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, name, email, hashed_password, role) VALUES (?, ?, ?, ?, ?)",
                (username, name, email, hashed_password, role)
            )
            conn.commit()
            success = True
        except sqlite3.IntegrityError as e:
            logger.error(f"Failed to create user {username}: {e}")
            success = False
        finally:
            conn.close()
    
    if success:
        try:
            log_security_event("USER_CREATED", username=username, details=f"User {username} created with role {role}")
        except:
            pass
    
    return success

def get_user(username: str) -> Optional[Dict[str, Any]]:
    """Get user by username"""
    with _db_lock:
        conn = sqlite3.connect(DB_NAME, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, name, email, hashed_password, role, is_active, is_verified, created_at, last_login, "
            "two_fa_enabled, failed_login_attempts, locked_until FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "username": row[0],
                "name": row[1],
                "email": row[2],
                "hashed_password": row[3],
                "role": row[4],
                "is_active": row[5],
                "is_verified": row[6],
                "created_at": row[7],
                "last_login": row[8],
                "two_fa_enabled": row[9],
                "failed_login_attempts": row[10],
                "locked_until": row[11]
            }
        return None

def update_user_login(username: str, success: bool = True):
    """Update user login information"""
    with _db_lock:
        conn = sqlite3.connect(DB_NAME, timeout=10.0)
        cursor = conn.cursor()
        
        if success:
            cursor.execute(
                "UPDATE users SET last_login = ?, failed_login_attempts = 0, locked_until = NULL WHERE username = ?",
                (datetime.now(), username)
            )
        else:
            cursor.execute(
                "UPDATE users SET failed_login_attempts = failed_login_attempts + 1 WHERE username = ?",
                (username,)
            )
            
            # Lock account after 5 failed attempts for 15 minutes
            cursor.execute("SELECT failed_login_attempts FROM users WHERE username = ?", (username,))
            attempts = cursor.fetchone()
            if attempts and attempts[0] >= 5:
                lock_until = datetime.now() + timedelta(minutes=15)
                cursor.execute(
                    "UPDATE users SET locked_until = ? WHERE username = ?",
                    (lock_until, username)
                )
        
        conn.commit()
        conn.close()
        
    # Log after database transaction completes
    try:
        if success:
            log_security_event("LOGIN_SUCCESS", username=username)
        else:
            log_security_event("LOGIN_FAILED", username=username)
    except:
        pass  # Don't fail login if logging fails

def is_user_locked(username: str) -> bool:
    """Check if user account is locked"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT locked_until FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if row and row[0]:
        locked_until = datetime.fromisoformat(row[0])
        return datetime.now() < locked_until
    return False

def update_user_password(username: str, new_hashed_password: str):
    """Update user password"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET hashed_password = ?, reset_token = NULL, reset_token_expires = NULL WHERE username = ?",
        (new_hashed_password, username)
    )
    conn.commit()
    conn.close()
    log_security_event("PASSWORD_CHANGED", username=username)

def set_password_reset_token(username: str, token: str, expires_at: datetime):
    """Set password reset token for user"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET reset_token = ?, reset_token_expires = ? WHERE username = ?",
        (token, expires_at, username)
    )
    conn.commit()
    conn.close()
    log_security_event("PASSWORD_RESET_REQUESTED", username=username)

def verify_reset_token(token: str) -> Optional[str]:
    """Verify password reset token and return username if valid"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username FROM users WHERE reset_token = ? AND reset_token_expires > ?",
        (token, datetime.now())
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_all_users(include_inactive: bool = False) -> List[Dict[str, Any]]:
    """Get all users for admin management"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    query = "SELECT username, name, email, role, is_active, is_verified, created_at, last_login FROM users"
    if not include_inactive:
        query += " WHERE is_active = 1"
    query += " ORDER BY created_at DESC"
    
    cursor.execute(query)
    users = []
    for row in cursor.fetchall():
        users.append({
            "username": row[0],
            "name": row[1],
            "email": row[2],
            "role": row[3],
            "is_active": row[4],
            "is_verified": row[5],
            "created_at": row[6],
            "last_login": row[7]
        })
    conn.close()
    return users

def update_user_role(username: str, new_role: str, admin_username: str):
    """Update user role (admin only)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role = ? WHERE username = ?", (new_role, username))
    conn.commit()
    conn.close()
    log_security_event("ROLE_CHANGED", username=username, details=f"Role changed to {new_role} by {admin_username}")

def deactivate_user(username: str, admin_username: str):
    """Deactivate user account (admin only)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_active = 0 WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    log_security_event("USER_DEACTIVATED", username=username, details=f"Deactivated by {admin_username}")

def activate_user(username: str, admin_username: str):
    """Activate user account (admin only)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_active = 1 WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    log_security_event("USER_ACTIVATED", username=username, details=f"Activated by {admin_username}")

def approve_pending_user(username: str, admin_username: str) -> bool:
    """Approve a pending user and move them to active users"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # Get pending user data
        cursor.execute(
            "SELECT username, name, email, hashed_password FROM pending_users WHERE username = ?",
            (username,)
        )
        pending_user = cursor.fetchone()
        
        if not pending_user:
            return False
        
        # Create active user
        cursor.execute(
            "INSERT INTO users (username, name, email, hashed_password, role, is_verified) VALUES (?, ?, ?, ?, 'user', 1)",
            pending_user
        )
        
        # Remove from pending
        cursor.execute("DELETE FROM pending_users WHERE username = ?", (username,))
        
        conn.commit()
        log_security_event("USER_APPROVED", username=username, details=f"Approved by {admin_username}")
        return True
    except Exception as e:
        logger.error(f"Failed to approve user {username}: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def save_user_preference(username: str, key: str, value: Any):
    """Save user preference to database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    value_json = json.dumps(value) if value is not None else None
    
    cursor.execute(
        "INSERT OR REPLACE INTO user_preferences (username, preference_key, preference_value, updated_at) VALUES (?, ?, ?, ?)",
        (username, key, value_json, datetime.now())
    )
    conn.commit()
    conn.close()

def get_user_preferences(username: str) -> Dict[str, Any]:
    """Get all user preferences from database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT preference_key, preference_value FROM user_preferences WHERE username = ?",
        (username,)
    )
    
    preferences = {}
    for row in cursor.fetchall():
        key, value_json = row
        try:
            preferences[key] = json.loads(value_json) if value_json else None
        except json.JSONDecodeError:
            preferences[key] = value_json
    
    conn.close()
    return preferences

def log_security_event(event_type: str, username: str = None, ip_address: str = None, user_agent: str = None, details: str = None):
    """Log security events to database"""
    try:
        with _db_lock:
            conn = sqlite3.connect(DB_NAME, timeout=10.0)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO security_logs (event_type, username, ip_address, user_agent, details) VALUES (?, ?, ?, ?, ?)",
                (event_type, username, ip_address, user_agent, details)
            )
            conn.commit()
            conn.close()
    except Exception as e:
        logger.error(f"Failed to log security event: {e}")

def get_security_logs(limit: int = 100) -> List[Dict[str, Any]]:
    """Get security logs for admin review"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT event_type, username, ip_address, user_agent, details, timestamp FROM security_logs ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    )
    
    logs = []
    for row in cursor.fetchall():
        logs.append({
            "event_type": row[0],
            "username": row[1],
            "ip_address": row[2],
            "user_agent": row[3],
            "details": row[4],
            "timestamp": row[5]
        })
    
    conn.close()
    return logs