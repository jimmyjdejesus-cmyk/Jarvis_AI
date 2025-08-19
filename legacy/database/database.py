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
    # User settings table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS user_settings
                   (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT NOT NULL,
                       settings_json TEXT,
                       created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                       updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                       UNIQUE(username),
                       FOREIGN KEY (username) REFERENCES users (username)
                   )
                   ''')

    # API/Model call analytics table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS api_call_analytics
                   (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT NOT NULL,
                       session_id INTEGER,
                       endpoint_type TEXT NOT NULL,
                       model_name TEXT,
                       prompt_tokens INTEGER,
                       response_tokens INTEGER,
                       latency_ms INTEGER,
                       success BOOLEAN NOT NULL,
                       error_type TEXT,
                       error_message TEXT,
                       timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY (username) REFERENCES users (username),
                       FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
                   )
                   ''')

    # User feedback table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS user_feedback
                   (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT NOT NULL,
                       feedback_type TEXT NOT NULL,
                       rating INTEGER,
                       title TEXT,
                       description TEXT NOT NULL,
                       category TEXT,
                       priority TEXT DEFAULT 'medium',
                       status TEXT DEFAULT 'open',
                       assigned_to TEXT,
                       resolved_at DATETIME,
                       created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                       updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY (username) REFERENCES users (username)
                   )
                   ''')

    # Feature usage analytics table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS feature_analytics
                   (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT NOT NULL,
                       feature_name TEXT NOT NULL,
                       action TEXT NOT NULL,
                       metadata TEXT,
                       session_id INTEGER,
                       timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY (username) REFERENCES users (username),
                       FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
                   )
                   ''')

    # Error tracking table
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS error_analytics
                   (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT,
                       session_id INTEGER,
                       error_type TEXT NOT NULL,
                       error_code TEXT,
                       error_message TEXT NOT NULL,
                       stack_trace TEXT,
                       context TEXT,
                       resolved BOOLEAN DEFAULT 0,
                       resolved_at DATETIME,
                       timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                       FOREIGN KEY (username) REFERENCES users (username),
                       FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
                   )
                   ''')

    # User activity summary table for quick analytics
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS user_activity_summary
                   (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username TEXT NOT NULL,
                       date DATE NOT NULL,
                       total_sessions INTEGER DEFAULT 0,
                       total_messages INTEGER DEFAULT 0,
                       total_api_calls INTEGER DEFAULT 0,
                       total_tokens_used INTEGER DEFAULT 0,
                       avg_latency_ms REAL DEFAULT 0,
                       error_count INTEGER DEFAULT 0,
                       feature_usage_count INTEGER DEFAULT 0,
                       created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                       updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                       UNIQUE(username, date),
                       FOREIGN KEY (username) REFERENCES users (username)
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

def update_user(username: str, **kwargs):
    """
    Update user information in the database
    
    Args:
        username: Username of the user to update
        **kwargs: Key-value pairs of fields to update
    """
    if not kwargs:
        return False
    
    allowed_fields = [
        'name', 'email', 'role', 'is_active', 'locked_until', 
        'password_hash', 'reset_token', 'reset_token_expiry',
        'two_fa_enabled', 'two_fa_secret', 'two_fa_pending'
    ]
    
    # Filter out any fields that aren't in allowed_fields
    valid_updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not valid_updates:
        return False
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # Build SET clause for SQL query
        set_clause = ', '.join([f"{key} = ?" for key in valid_updates.keys()])
        values = list(valid_updates.values())
        values.append(username)  # For the WHERE clause
        
        # Execute update
        cursor.execute(
            f"UPDATE users SET {set_clause} WHERE username = ?",
            values
        )
        
        conn.commit()
        result = cursor.rowcount > 0
        conn.close()
        return result
    except Exception as e:
        conn.rollback()
        conn.close()
        logger.error(f"Failed to update user {username}: {e}")
        return False

def update_user_field(username: str, field: str, value):
    """
    Update a specific field for a user
    
    Args:
        username: Username of the user to update
        field: Field name to update
        value: New value for the field
    """
    return update_user(username, **{field: value})

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
    print(f"[DEBUG] save_user_preference: username={username}, key={key}, value_json={value_json}, time={datetime.now()}")
    try:
        cursor.execute(
            "INSERT OR REPLACE INTO user_preferences (username, preference_key, preference_value, updated_at) VALUES (?, ?, ?, ?)",
            (username, key, value_json, datetime.now())
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"[ERROR] IntegrityError in save_user_preference: {e}")
        raise
    finally:
        conn.close()

# User settings CRUD
def save_user_settings(username: str, settings: Dict[str, Any]):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    settings_json = json.dumps(settings)
    cursor.execute(
        "INSERT OR REPLACE INTO user_settings (username, settings_json, updated_at) VALUES (?, ?, ?)",
        (username, settings_json, datetime.now())
    )
    conn.commit()
    conn.close()

def get_user_settings(username: str) -> Dict[str, Any]:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT settings_json FROM user_settings WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        try:
            return json.loads(row[0])
        except Exception:
            return {}
    return {}

    # ...existing code...

# Backup/export/import utilities
def backup_user_data(username: str = None) -> str:
    """Export all user data (preferences, settings, chat logs) as a JSON file
    If username is None, backs up all users"""
    
    # Get all users if username not specified
    if username is None:
        all_users = get_all_users()
        usernames = [user["username"] for user in all_users]
    else:
        usernames = [username]
    
    # Initialize data structure
    backup_data = {
        "users": [],
        "preferences": [],
        "settings": []
    }
    
    # Get data for each user
    for user in usernames:
        backup_data["users"].append(get_user(user))
        backup_data["preferences"].append({"username": user, "preferences": get_user_preferences(user)})
        backup_data["settings"].append({"username": user, "settings": get_user_settings(user)})
    
    # Create backup file
    import os
    import json
    from datetime import datetime
    
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)
    backup_file = os.path.join(backup_dir, f"jarvis_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    with open(backup_file, "w") as f:
        json.dump(backup_data, f, indent=2)
    
    return backup_file
    cursor.execute("SELECT id, project_name, session_name, timestamp FROM chat_sessions WHERE username = ?", (username,))
    sessions = cursor.fetchall()
    for s in sessions:
        session = {"id": s[0], "project_name": s[1], "session_name": s[2], "timestamp": s[3]}
        data["chat_sessions"].append(session)
        cursor.execute("SELECT role, content, sources, timestamp FROM chat_logs WHERE session_id = ?", (s[0],))
        logs = cursor.fetchall()
        for l in logs:
            data["chat_logs"].append({"session_id": s[0], "role": l[0], "content": l[1], "sources": l[2], "timestamp": l[3]})
    conn.close()
    return data

def import_user_data(username: str, data: Dict[str, Any]):
    """Import user data (preferences, settings, chat logs) from dict"""
    save_user_settings(username, data.get("settings", {}))
    for k, v in data.get("preferences", {}).items():
        save_user_preference(username, k, v)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for session in data.get("chat_sessions", []):
        cursor.execute("INSERT OR IGNORE INTO chat_sessions (id, username, project_name, session_name, timestamp) VALUES (?, ?, ?, ?, ?)",
                       (session["id"], username, session["project_name"], session["session_name"], session["timestamp"]))
    for log in data.get("chat_logs", []):
        cursor.execute("INSERT INTO chat_logs (session_id, role, content, sources, timestamp) VALUES (?, ?, ?, ?, ?)",
                       (log["session_id"], log["role"], log["content"], log["sources"], log["timestamp"]))
    conn.commit()
    conn.close()

    # Cloud DB support
    import os
    def get_db_connection():
        db_url = os.getenv("JANUS_DB_URL")
        if db_url:
            return sqlite3.connect(db_url)
        return sqlite3.connect(DB_NAME)

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


# Analytics and Feedback Functions

def log_api_call(username: str, session_id: int = None, endpoint_type: str = None, 
                model_name: str = None, prompt_tokens: int = None, response_tokens: int = None,
                latency_ms: int = None, success: bool = True, error_type: str = None, 
                error_message: str = None):
    """Log API/model call analytics"""
    try:
        with _db_lock:
            conn = sqlite3.connect(DB_NAME, timeout=10.0)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO api_call_analytics 
                (username, session_id, endpoint_type, model_name, prompt_tokens, 
                 response_tokens, latency_ms, success, error_type, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, session_id, endpoint_type, model_name, prompt_tokens,
                  response_tokens, latency_ms, success, error_type, error_message))
            conn.commit()
            conn.close()
    except Exception as e:
        logger.error(f"Failed to log API call: {e}")


def log_feature_usage(username: str, feature_name: str, action: str, 
                     metadata: Dict = None, session_id: int = None):
    """Log feature usage analytics"""
    try:
        with _db_lock:
            conn = sqlite3.connect(DB_NAME, timeout=10.0)
            cursor = conn.cursor()
            metadata_json = json.dumps(metadata) if metadata else None
            cursor.execute('''
                INSERT INTO feature_analytics (username, feature_name, action, metadata, session_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, feature_name, action, metadata_json, session_id))
            conn.commit()
            conn.close()
    except Exception as e:
        logger.error(f"Failed to log feature usage: {e}")


def log_error(username: str = None, session_id: int = None, error_type: str = None,
              error_code: str = None, error_message: str = None, stack_trace: str = None,
              context: Dict = None):
    """Log error analytics"""
    try:
        with _db_lock:
            conn = sqlite3.connect(DB_NAME, timeout=10.0)
            cursor = conn.cursor()
            context_json = json.dumps(context) if context else None
            cursor.execute('''
                INSERT INTO error_analytics 
                (username, session_id, error_type, error_code, error_message, stack_trace, context)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, session_id, error_type, error_code, error_message, stack_trace, context_json))
            conn.commit()
            conn.close()
    except Exception as e:
        logger.error(f"Failed to log error: {e}")


def save_user_feedback(username: str, feedback_type: str, description: str,
                      rating: int = None, title: str = None, category: str = None,
                      priority: str = "medium"):
    """Save user feedback"""
    try:
        with _db_lock:
            conn = sqlite3.connect(DB_NAME, timeout=10.0)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_feedback 
                (username, feedback_type, rating, title, description, category, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, feedback_type, rating, title, description, category, priority))
            conn.commit()
            conn.close()
            return True
    except Exception as e:
        logger.error(f"Failed to save user feedback: {e}")
        return False


def get_analytics_overview(days: int = 30) -> Dict[str, Any]:
    """Get analytics overview for the last N days"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Total API calls
        cursor.execute('''
            SELECT COUNT(*), AVG(latency_ms), SUM(prompt_tokens), SUM(response_tokens)
            FROM api_call_analytics WHERE timestamp >= ?
        ''', (since_date,))
        api_stats = cursor.fetchone()
        
        # Error statistics
        cursor.execute('''
            SELECT COUNT(*) FROM api_call_analytics 
            WHERE timestamp >= ? AND success = 0
        ''', (since_date,))
        error_count = cursor.fetchone()[0]
        
        # Active users
        cursor.execute('''
            SELECT COUNT(DISTINCT username) FROM api_call_analytics 
            WHERE timestamp >= ?
        ''', (since_date,))
        active_users = cursor.fetchone()[0]
        
        # Popular features
        cursor.execute('''
            SELECT feature_name, COUNT(*) as usage_count
            FROM feature_analytics WHERE timestamp >= ?
            GROUP BY feature_name ORDER BY usage_count DESC LIMIT 10
        ''', (since_date,))
        popular_features = cursor.fetchall()
        
        # Recent feedback
        cursor.execute('''
            SELECT COUNT(*) FROM user_feedback WHERE created_at >= ?
        ''', (since_date,))
        feedback_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_api_calls": api_stats[0] or 0,
            "avg_latency_ms": api_stats[1] or 0,
            "total_prompt_tokens": api_stats[2] or 0,
            "total_response_tokens": api_stats[3] or 0,
            "error_count": error_count,
            "active_users": active_users,
            "popular_features": popular_features,
            "feedback_count": feedback_count,
            "days": days
        }
    except Exception as e:
        logger.error(f"Failed to get analytics overview: {e}")
        return {}


def get_user_feedback(limit: int = 50, status: str = None) -> List[Dict[str, Any]]:
    """Get user feedback with optional status filter"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        query = '''
            SELECT id, username, feedback_type, rating, title, description, 
                   category, priority, status, created_at, updated_at
            FROM user_feedback
        '''
        params = []
        
        if status:
            query += ' WHERE status = ?'
            params.append(status)
            
        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        
        feedback = []
        for row in cursor.fetchall():
            feedback.append({
                "id": row[0],
                "username": row[1],
                "feedback_type": row[2],
                "rating": row[3],
                "title": row[4],
                "description": row[5],
                "category": row[6],
                "priority": row[7],
                "status": row[8],
                "created_at": row[9],
                "updated_at": row[10]
            })
        
        conn.close()
        return feedback
    except Exception as e:
        logger.error(f"Failed to get user feedback: {e}")
        return []


def update_feedback_status(feedback_id: int, status: str, assigned_to: str = None):
    """Update feedback status"""
    try:
        with _db_lock:
            conn = sqlite3.connect(DB_NAME, timeout=10.0)
            cursor = conn.cursor()
            
            update_fields = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
            params = [status]
            
            if assigned_to:
                update_fields.append("assigned_to = ?")
                params.append(assigned_to)
            
            if status in ['resolved', 'closed']:
                update_fields.append("resolved_at = CURRENT_TIMESTAMP")
            
            params.append(feedback_id)
            
            query = f"UPDATE user_feedback SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            return True
    except Exception as e:
        logger.error(f"Failed to update feedback status: {e}")
        return False


def get_error_analytics(days: int = 7) -> List[Dict[str, Any]]:
    """Get error analytics for the last N days"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        since_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute('''
            SELECT error_type, error_code, COUNT(*) as count, 
                   MAX(timestamp) as latest_occurrence
            FROM error_analytics 
            WHERE timestamp >= ?
            GROUP BY error_type, error_code
            ORDER BY count DESC
        ''', (since_date,))
        
        errors = []
        for row in cursor.fetchall():
            errors.append({
                "error_type": row[0],
                "error_code": row[1],
                "count": row[2],
                "latest_occurrence": row[3]
            })
        
        conn.close()
        return errors
    except Exception as e:
        logger.error(f"Failed to get error analytics: {e}")
        return []


def update_user_activity_summary(username: str, date: str = None):
    """Update or create user activity summary for a specific date"""
    if not date:
        date = datetime.now().date().isoformat()
    
    try:
        with _db_lock:
            conn = sqlite3.connect(DB_NAME, timeout=10.0)
            cursor = conn.cursor()
            
            # Get stats for the date
            cursor.execute('''
                SELECT COUNT(DISTINCT session_id), COUNT(*), AVG(latency_ms), 
                       SUM(prompt_tokens + response_tokens), 
                       SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END)
                FROM api_call_analytics 
                WHERE username = ? AND DATE(timestamp) = ?
            ''', (username, date))
            api_stats = cursor.fetchone()
            
            cursor.execute('''
                SELECT COUNT(*) FROM feature_analytics
                WHERE username = ? AND DATE(timestamp) = ?
            ''', (username, date))
            feature_usage = cursor.fetchone()[0]
            
            # Insert or update summary
            cursor.execute('''
                INSERT OR REPLACE INTO user_activity_summary
                (username, date, total_sessions, total_api_calls, avg_latency_ms, 
                 total_tokens_used, error_count, feature_usage_count, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (username, date, api_stats[0] or 0, api_stats[1] or 0, 
                  api_stats[2] or 0, api_stats[3] or 0, api_stats[4] or 0, feature_usage))
            
            conn.commit()
            conn.close()
    except Exception as e:
        logger.error(f"Failed to update user activity summary: {e}")