"""
Database module for Jarvis AI
Provides database operations and user management functionality
"""

from pathlib import Path

# Import all database functions from legacy implementation
try:
    from database.database import *
    from database.analytics_functions import *
except ImportError as e:
    # Fallback imports
    print(f"Warning: Could not import legacy database: {e}")
    
    # Create minimal fallback functions
    def init_db():
        """Initialize database - fallback implementation"""
        import sqlite3
        conn = sqlite3.connect('janus_database.db')
        cursor = conn.cursor()
        
        # Create basic users table
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
                last_login DATETIME
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_user(username):
        """Get user - fallback implementation"""
        import sqlite3
        conn = sqlite3.connect('janus_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, result))
        return None
    
    def get_user_preferences(username):
        """Get user preferences - fallback implementation"""
        return {}
    
    def save_user_preference(username, key, value):
        """Save user preference - fallback implementation"""
        pass
    
    def get_user_settings(username):
        """Get user settings - fallback implementation"""
        return {}