# Backup and Restore Functionality

## Overview

Jarvis AI includes comprehensive backup and restore functionality for both individual users and system administrators. This allows users to safeguard their data and preferences, and easily transfer them between different installations of Jarvis AI.

## User-Level Backup and Restore

### Creating a Backup

As a user, you can back up all your personal data by following these steps:

1. Log in to your Jarvis AI account
2. In the sidebar, locate the "Data Management" section
3. Click the "Backup My Data" button
4. The system will create a ZIP file containing all your:
   - User preferences
   - Conversation history
   - Custom settings
   - Uploaded files (if any)
5. You'll see a success message with the path to your backup file

The backup file is saved in the `backups` directory with a name like `user_backup_username_YYYYMMDD_HHMMSS.zip`.

### Restoring from a Backup

To restore your data from a previous backup:

1. Log in to your Jarvis AI account
2. In the sidebar, locate the "Data Management" section
3. Click "Browse..." under "Import Personal Backup" and select your backup ZIP file
4. Choose whether to overwrite existing data:
   - Check "Overwrite existing data" if you want to replace your current data
   - Leave it unchecked to keep your current data where it doesn't conflict
5. Click the "Restore My Data" button
6. Wait for the restoration process to complete

## Admin-Level Backup and Restore

System administrators have additional capabilities for backing up all users' data.

### System-Wide Backup

As an admin:

1. Log in with an admin account
2. In the sidebar, locate the "Admin Tools" section
3. Under "System Backup & Restore", click "Backup All Users"
4. The system will create a JSON file with all system data
5. You'll see a success message with the path to the backup file

### System-Wide Restore

To restore from a system backup:

1. Log in with an admin account
2. In the sidebar, locate the "Admin Tools" section
3. Under "System Backup & Restore", click "Browse..." and select your JSON backup file
4. Click "Restore System Data"
5. Wait for the restoration process to complete

## Backup File Structure

### User Backup (ZIP)

The user backup ZIP file contains:

- `user_data.json` - A JSON file with user settings, preferences, and conversation history
- User files (if any) - Organized in directories matching their original structure

### System Backup (JSON)

The system backup JSON file contains:

- `users` - Basic user information (excluding password hashes)
- `preferences` - All user preferences
- `settings` - System-wide settings

## Best Practices

1. **Regular Backups**: Create backups regularly, especially before system updates
2. **Secure Storage**: Store backup files in a secure location
3. **Naming Convention**: Consider adding descriptive names to backup files for easier identification
4. **Version Compatibility**: Ensure Jarvis AI versions are compatible when restoring backups

## Troubleshooting

If you encounter issues with the backup or restore process:

1. Check that the backup file is not corrupted
2. Verify you have sufficient permissions
3. For admins: Ensure database schema compatibility
4. Contact system administrator if issues persist
