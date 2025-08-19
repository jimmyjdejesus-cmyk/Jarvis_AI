"""Additional database functions to support file uploads and backups"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, List

DB_NAME = 'janus_database.db'

def get_all_users():
    """Get all users in the database"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username, name, email, role, is_active FROM users")
    users = []
    for row in cursor.fetchall():
        users.append({
            "username": row[0],
            "name": row[1],
            "email": row[2],
            "role": row[3],
            "is_active": row[4]
        })
    conn.close()
    return users

def backup_all_user_data():
    """Export all user data as a JSON file"""
    from database.database import get_user, get_user_preferences, get_user_settings
    
    # Get all users
    all_users = get_all_users()
    usernames = [user["username"] for user in all_users]
    
    # Initialize data structure
    backup_data = {
        "users": [],
        "preferences": [],
        "settings": []
    }
    
    # Get data for each user
    for username in usernames:
        user_data = get_user(username)
        if user_data:
            # Remove password hash for security
            user_data.pop('hashed_password', None)
            backup_data["users"].append(user_data)
            backup_data["preferences"].append({
                "username": username, 
                "preferences": get_user_preferences(username)
            })
            backup_data["settings"].append({
                "username": username, 
                "settings": get_user_settings(username)
            })
    
    # Create backup file
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)
    backup_file = os.path.join(backup_dir, f"jarvis_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    with open(backup_file, "w") as f:
        json.dump(backup_data, f, indent=2)
    
    return backup_file

def backup_user_data(username):
    """
    Create a backup of a single user's data including preferences and history.
    
    Args:
        username: The username of the user to backup
        
    Returns:
        Path to the created backup file
    """
    from database.database import get_user, get_user_preferences, get_user_settings
    import shutil
    from pathlib import Path
    from zipfile import ZipFile, ZIP_DEFLATED
    
    try:
        # Create backup directory if it doesn't exist
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        # Create a timestamped backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"user_backup_{username}_{timestamp}.zip"
        backup_path = backup_dir / backup_filename
        
        # Get user data
        user_data = get_user(username)
        if not user_data:
            print(f"User {username} not found")
            return None
        
        # Remove password hash for security
        user_data.pop('hashed_password', None)
        
        # Get preferences and settings
        preferences = get_user_preferences(username)
        settings = get_user_settings(username)
        
        # Create JSON representations
        backup_data = {
            'user': user_data,
            'preferences': preferences,
            'settings': settings
        }
        
        # Connect to database for history data
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_id_result = cursor.fetchone()
        
        if user_id_result:
            user_id = user_id_result[0]
            # Get user history
            cursor.execute("SELECT * FROM conversation_history WHERE user_id = ?", (user_id,))
            user_history = cursor.fetchall()
            backup_data['history'] = user_history
        
        conn.close()
        
        # Create the ZIP file
        with ZipFile(backup_path, 'w', ZIP_DEFLATED) as zipf:
            # Add the JSON data
            zipf.writestr('user_data.json', json.dumps(backup_data, default=str))
            
            # Add any user files if they exist
            user_files_dir = Path(f"user_files/{username}")
            if user_files_dir.exists():
                for file_path in user_files_dir.rglob('*'):
                    if file_path.is_file():
                        zipf.write(file_path, file_path.relative_to(Path("user_files")))
        
        return str(backup_path)
    
    except Exception as e:
        print(f"Error creating backup for user {username}: {str(e)}")
        return None

def import_user_data_from_json(file_obj):
    """Import user data from uploaded JSON file object"""
    from database.database import save_user_preference, save_user_settings
    
    try:
        # Read and parse the uploaded JSON file
        backup_data = json.load(file_obj)
        
        # Initialize counters
        stats = {
            "users": 0,
            "preferences": 0,
            "settings": 0
        }
        
        # Import preferences
        if "preferences" in backup_data:
            for pref_data in backup_data["preferences"]:
                username = pref_data.get("username")
                preferences = pref_data.get("preferences", {})
                
                if username and preferences:
                    for key, value in preferences.items():
                        save_user_preference(username, key, value)
                        stats["preferences"] += 1
        
        # Import settings
        if "settings" in backup_data:
            for settings_data in backup_data["settings"]:
                username = settings_data.get("username")
                settings = settings_data.get("settings", {})
                
                if username and settings:
                    save_user_settings(username, settings)
                    stats["settings"] += 1
        
        return stats
    except Exception as e:
        print(f"Error importing user data: {e}")
        return {"error": str(e)}

def import_user_data(backup_file, overwrite=False):
    """
    Import user data from a backup ZIP file
    
    Args:
        backup_file: Path to the backup file
        overwrite: Whether to overwrite existing data (default: False)
        
    Returns:
        Dict with stats or error message
    """
    from database.database import save_user_preference, save_user_settings
    import shutil
    from pathlib import Path
    from zipfile import ZipFile
    
    try:
        # Check if file exists
        if not os.path.exists(backup_file):
            return {"error": f"Backup file not found: {backup_file}"}
        
        # Extract the backup
        temp_dir = Path("temp_restore")
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()
        
        # Initialize stats
        stats = {
            "user": 0,
            "preferences": 0,
            "settings": 0,
            "history": 0,
            "files": 0
        }
        
        with ZipFile(backup_file, 'r') as zipf:
            zipf.extractall(temp_dir)
        
        # Load the JSON data
        with open(temp_dir / "user_data.json", 'r') as f:
            backup_data = json.loads(f.read())
        
        # Get user info
        user_data = backup_data.get('user')
        if not user_data:
            shutil.rmtree(temp_dir)
            return {"error": "Invalid backup file format - missing user data"}
            
        username = user_data.get('username')
        if not username:
            shutil.rmtree(temp_dir)
            return {"error": "Invalid backup file format - missing username"}
        
        # Connect to database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()
        
        if existing_user and not overwrite:
            conn.close()
            shutil.rmtree(temp_dir)
            return {"error": f"User {username} already exists and overwrite is set to False"}
        
        # Import preferences
        if 'preferences' in backup_data:
            for key, value in backup_data['preferences'].items():
                save_user_preference(username, key, value)
                stats["preferences"] += 1
        
        # Import settings
        if 'settings' in backup_data:
            save_user_settings(username, backup_data['settings'])
            stats["settings"] += 1
        
        # Import history if user exists
        if existing_user and 'history' in backup_data:
            user_id = existing_user[0]
            
            # Begin transaction for history
            conn.execute("BEGIN TRANSACTION")
            
            try:
                # Delete existing history if overwrite is True
                if overwrite:
                    cursor.execute("DELETE FROM conversation_history WHERE user_id = ?", (user_id,))
                
                # Import history entries
                for hist in backup_data['history']:
                    if len(hist) >= 6:  # Make sure we have enough fields
                        cursor.execute(
                            "INSERT INTO conversation_history (user_id, timestamp, content, role, session_id) VALUES (?, ?, ?, ?, ?)",
                            (user_id, hist[2], hist[3], hist[4], hist[5])
                        )
                        stats["history"] += 1
                
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"Error importing history: {str(e)}")
        
        conn.close()
        
        # Copy user files if they exist
        user_files_source = temp_dir / username
        user_files_dest = Path(f"user_files/{username}")
        
        if user_files_source.exists():
            if user_files_dest.exists() and overwrite:
                shutil.rmtree(user_files_dest)
            
            user_files_dest.parent.mkdir(exist_ok=True)
            if user_files_source.exists():
                shutil.copytree(user_files_source, user_files_dest, dirs_exist_ok=True)
                
                # Count files
                stats["files"] = sum(1 for _ in user_files_dest.rglob('*') if _.is_file())
        
        # Cleanup
        shutil.rmtree(temp_dir)
        return stats
            
    except Exception as e:
        print(f"Error importing backup: {str(e)}")
        if os.path.exists("temp_restore"):
            shutil.rmtree("temp_restore")
        return {"error": str(e)}
