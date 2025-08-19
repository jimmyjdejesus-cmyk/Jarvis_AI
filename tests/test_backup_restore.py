#!/usr/bin/env python3

import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path for importing modules
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from database.admin_utils import backup_user_data, import_user_data, backup_all_user_data, import_user_data_from_json
from database.database import save_user_preference, get_user_preferences


def test_single_user_backup_restore():
    """Test backing up and restoring a single user's data"""
    print("\nTesting single user backup/restore...")
    
    # Set username for test
    test_user = "test_user"
    
    # Create some test data
    print(f"Creating test data for {test_user}...")
    test_prefs = {
        "theme": "dark",
        "model": "llama3",
        "draft_model": "None",
        "reasoning_display": "Expandable"
    }
    
    # Save test preferences
    for key, value in test_prefs.items():
        save_user_preference(test_user, key, value)
    
    # Verify preferences were saved
    saved_prefs = get_user_preferences(test_user)
    print(f"Saved preferences: {saved_prefs}")
    
    # Backup the user data
    print(f"Creating backup for {test_user}...")
    backup_path = backup_user_data(test_user)
    
    if not backup_path or not os.path.exists(backup_path):
        print(f"Failed to create backup at {backup_path}")
        return False
    
    print(f"Backup created at: {backup_path}")
    
    # Change the preferences
    print("Changing user preferences...")
    new_prefs = {
        "theme": "light",
        "model": "mistral",
        "draft_model": "mistral-light"
    }
    
    for key, value in new_prefs.items():
        save_user_preference(test_user, key, value)
    
    # Verify the changes
    changed_prefs = get_user_preferences(test_user)
    print(f"Changed preferences: {changed_prefs}")
    
    # Restore from backup
    print(f"Restoring from backup: {backup_path}")
    result = import_user_data(backup_path, overwrite=True)
    
    if isinstance(result, dict) and "error" in result:
        print(f"Error restoring data: {result['error']}")
        return False
    
    print(f"Restore results: {result}")
    
    # Verify restoration
    restored_prefs = get_user_preferences(test_user)
    print(f"Restored preferences: {restored_prefs}")
    
    # Check if the preferences match the original ones
    success = True
    for key, value in test_prefs.items():
        if restored_prefs.get(key) != value:
            print(f"Mismatch for {key}: expected {value}, got {restored_prefs.get(key)}")
            success = False
    
    if success:
        print("✅ Test passed: Single user backup and restore successful")
    else:
        print("❌ Test failed: Restored preferences don't match original")
    
    return success


def test_system_backup_restore():
    """Test backing up and restoring system-wide data"""
    print("\nTesting system-wide backup/restore...")
    
    # Create backup of all users
    print("Creating system-wide backup...")
    backup_path = backup_all_user_data()
    
    if not backup_path or not os.path.exists(backup_path):
        print(f"Failed to create system backup at {backup_path}")
        return False
    
    print(f"System backup created at: {backup_path}")
    
    # Create a temporary file to simulate upload
    with open(backup_path, 'rb') as f:
        backup_content = f.read()
    
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(backup_content)
        tmp_path = tmp_file.name
    
    # Import the data
    with open(tmp_path, 'rb') as f:
        try:
            print("Importing system backup...")
            result = import_user_data_from_json(f)
            print(f"Import results: {result}")
            print("✅ Test passed: System backup and restore successful")
            success = True
        except Exception as e:
            print(f"❌ Test failed: Error importing system data: {e}")
            success = False
    
    # Clean up
    os.unlink(tmp_path)
    return success


def main():
    """Run all tests"""
    print("Starting backup and restore tests")
    
    results = []
    
    # Test single user backup/restore
    results.append(test_single_user_backup_restore())
    
    # Test system-wide backup/restore
    results.append(test_system_backup_restore())
    
    # Print overall results
    print("\n=== Test Results ===")
    if all(results):
        print("✅ All tests passed!")
    else:
        print(f"❌ {results.count(False)} test(s) failed.")


if __name__ == "__main__":
    main()
