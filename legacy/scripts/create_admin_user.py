#!/usr/bin/env python3
"""Script to create an admin user for testing"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import database
from agent.features.security import hash_password

def create_admin_user():
    """Create admin user for testing"""
    
    print("Initializing database...")
    database.init_db()
    
    # Create admin user
    admin_data = {
        'username': 'admin',
        'name': 'Admin User',
        'email': 'admin@example.com',
        'password': 'admin123',  # Simple password for testing
        'role': 'admin'
    }
    
    try:
        hashed_password = hash_password(admin_data['password'])
        success = database.create_user(
            username=admin_data['username'],
            name=admin_data['name'],
            email=admin_data['email'],
            hashed_password=hashed_password,
            role=admin_data['role']
        )
        
        if success:
            print(f"Admin user created successfully!")
            print(f"Username: {admin_data['username']}")
            print(f"Password: {admin_data['password']}")
            print(f"Role: {admin_data['role']}")
        else:
            print("Admin user already exists or creation failed")
            
    except Exception as e:
        print(f"Error creating admin user: {e}")

    # Also create a regular test user
    test_user_data = {
        'username': 'testuser',
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'test123',
        'role': 'user'
    }
    
    try:
        hashed_password = hash_password(test_user_data['password'])
        success = database.create_user(
            username=test_user_data['username'],
            name=test_user_data['name'],
            email=test_user_data['email'],
            hashed_password=hashed_password,
            role=test_user_data['role']
        )
        
        if success:
            print(f"Test user created successfully!")
            print(f"Username: {test_user_data['username']}")
            print(f"Password: {test_user_data['password']}")
            print(f"Role: {test_user_data['role']}")
        else:
            print("Test user already exists or creation failed")
            
    except Exception as e:
        print(f"Error creating test user: {e}")

if __name__ == "__main__":
    create_admin_user()