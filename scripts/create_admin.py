"""
Script to create an admin user for Jarvis AI
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from agent.features.security import hash_password

DB_NAME = 'janus_database.db'

def create_admin_user(username, password, name, email):
    """Create an admin user in the database"""
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
    
    print(f"Admin user '{username}' created successfully!")

if __name__ == "__main__":
    print("Create Jarvis AI Admin User")
    print("--------------------------")
    
    # Get user input
    username = input("Username: ")
    password = input("Password: ")
    name = input("Full Name: ")
    email = input("Email: ")
    
    # Create the admin user
    create_admin_user(username, password, name, email)
