#!/usr/bin/env python3
"""
Migration script to move hardcoded users from app.py to database
"""

import database
from agent.security import hash_password

def migrate_hardcoded_users():
    """Migrate the hardcoded users to the database with proper bcrypt hashing"""
    
    # Initialize database
    database.init_db()
    
    # Hardcoded users from app.py
    users_to_migrate = [
        {
            "username": "Moodeux",
            "name": "Admin User",
            "email": "admin@jarvis.ai",
            "password": "Passcode",
            "role": "admin"
        },
        {
            "username": "jimmyjdejesus-cmyk",
            "name": "Jimmy De Jesus",
            "email": "jimmy@jarvis.ai",
            "password": "your_password_here",
            "role": "admin"
        }
    ]
    
    migrated = 0
    for user_data in users_to_migrate:
        # Check if user already exists
        existing_user = database.get_user(user_data["username"])
        if existing_user:
            print(f"User {user_data['username']} already exists, skipping...")
            continue
        
        # Hash password with bcrypt
        hashed_password = hash_password(user_data["password"])
        
        # Create user in database
        success = database.create_user(
            username=user_data["username"],
            name=user_data["name"],
            email=user_data["email"],
            hashed_password=hashed_password,
            role=user_data["role"]
        )
        
        if success:
            print(f"Successfully migrated user: {user_data['username']}")
            migrated += 1
        else:
            print(f"Failed to migrate user: {user_data['username']}")
    
    print(f"\nMigration complete. Migrated {migrated} users.")
    
    # Verify users can authenticate
    print("\nTesting authentication:")
    from agent.security import verify_password
    
    for user_data in users_to_migrate:
        user = database.get_user(user_data["username"])
        if user:
            can_auth = verify_password(user_data["password"], user["hashed_password"])
            print(f"  {user_data['username']}: {'✓' if can_auth else '✗'}")

if __name__ == "__main__":
    migrate_hardcoded_users()