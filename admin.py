import sqlite3
import bcrypt
from datetime import datetime

conn = sqlite3.connect('janus_database.db')
cursor = conn.cursor()

# Hash password with bcrypt
password = 'admin123'
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Insert admin user
cursor.execute('''
INSERT OR REPLACE INTO users 
(username, name, email, hashed_password, role, is_active, is_verified, created_at) 
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', ('admin', 'Administrator', 'admin@example.com', hashed, 'admin', 1, 1, datetime.now().isoformat()))

conn.commit()
conn.close()

print(f"Admin user created with username: admin and password: {password}")
