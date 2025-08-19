"""
Create an admin user with hardcoded values
"""
import sqlite3
import bcrypt

# Connect to the database
conn = sqlite3.connect('janus_database.db')
cursor = conn.cursor()

# Create the users table if it doesn't exist
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

# Create an admin user
username = 'admin'
password = 'password123'
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Insert the admin user
cursor.execute('''
INSERT OR REPLACE INTO users 
(username, name, email, hashed_password, role, is_active, is_verified, created_at) 
VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
''', (username, 'Administrator', 'admin@example.com', hashed, 'admin', 1, 1))

# Commit the changes
conn.commit()
conn.close()

print(f"Created admin user: {username} with password: {password}")
