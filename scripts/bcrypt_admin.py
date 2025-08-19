"""
Create an admin user for testing
"""
import sqlite3
from datetime import datetime
import bcrypt

DB_NAME = 'janus_database.db'

# Create a default admin user
username = "admin"
password = "Admin123!"
name = "Administrator"
email = "admin@jarvisai.local"

# Hash the password with bcrypt
salt = bcrypt.gensalt()
hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

# Connect to the database
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

print(f"Admin user '{username}' created with password '{password}'")
