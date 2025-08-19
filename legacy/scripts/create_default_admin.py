"""
Script to create a default admin user for Jarvis AI without interaction
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from agent.features.security import hash_password

DB_NAME = 'janus_database.db'

def create_default_admin():
    """Create a default admin user in the database"""
    username = "admin"
    password = "Admin123!"
    name = "Administrator"
    email = "admin@jarvisai.local"
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Make sure users table exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            name TEXT,
            email TEXT UNIQUE,
            hashed_password TEXT,
            role TEXT DEFAULT 'user',
            is_active INTEGER DEFAULT 1,
            is_verified INTEGER DEFAULT 0,
            created_at TEXT,
            last_login TEXT,
            two_fa_enabled INTEGER DEFAULT 0,
            two_fa_secret TEXT,
            two_fa_pending INTEGER DEFAULT 0,
            failed_login_attempts INTEGER DEFAULT 0,
            locked_until TEXT
        )
    ''')
    
    # Hash the password
    hashed_password = hash_password(password)
    
    # Create timestamp
    timestamp = datetime.now().isoformat()
    
    # Insert the admin user
    cursor.execute(
        "INSERT OR REPLACE INTO users (username, name, email, hashed_password, role, is_active, is_verified, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (username, name, email, hashed_password, "admin", 1, 1, timestamp)
    )
    
    conn.commit()
    conn.close()
    
    print(f"Default admin user '{username}' created with password '{password}'")

if __name__ == "__main__":
    create_default_admin()
