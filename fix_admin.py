"""
Script to recreate the admin user with known credentials
"""

import sqlite3
import os
import sys
from datetime import datetime
import bcrypt

# Database settings
DB_PATH = 'janus_database.db'

def hash_password(password):
    """Hash password using bcrypt for secure storage"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def recreate_admin():
    """Create or update the admin user with known credentials"""
    username = "admin"
    password = "Admin123!"  # Using a strong default password
    name = "Administrator"
    email = "admin@jarvisai.local"
    
    # Make sure database exists
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if the users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("Users table doesn't exist yet. Creating...")
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
                    reset_token TEXT,
                    reset_token_expires DATETIME,
                    two_fa_secret TEXT,
                    two_fa_enabled BOOLEAN DEFAULT 0,
                    failed_login_attempts INTEGER DEFAULT 0,
                    locked_until DATETIME
                )
            ''')
        
        # Hash the password
        hashed_password = hash_password(password)
        
        # Create timestamp
        timestamp = datetime.now().isoformat()
        
        # Check if user exists
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            # Update existing user
            cursor.execute("""
                UPDATE users 
                SET name = ?, 
                    email = ?, 
                    hashed_password = ?, 
                    role = 'admin', 
                    is_active = 1, 
                    is_verified = 1,
                    failed_login_attempts = 0,
                    locked_until = NULL
                WHERE username = ?
            """, (name, email, hashed_password, username))
            action = "updated"
        else:
            # Insert new user
            cursor.execute("""
                INSERT INTO users 
                (username, name, email, hashed_password, role, is_active, is_verified, created_at) 
                VALUES (?, ?, ?, ?, 'admin', 1, 1, ?)
            """, (username, name, email, hashed_password, timestamp))
            action = "created"
        
        conn.commit()
        print(f"✅ Admin user '{username}' {action} successfully!")
        print(f"👤 Username: {username}")
        print(f"🔑 Password: {password}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🛠️ Fixing Admin User for Jarvis AI")
    print("==================================")
    
    success = recreate_admin()
    
    if success:
        print("\n✅ Admin user setup complete!")
        print("🚀 You can now log in with username 'admin' and password 'Admin123!'")
    else:
        print("\n❌ Failed to setup admin user.")
