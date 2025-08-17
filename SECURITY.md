# Jarvis AI Security System

This document describes the comprehensive security and authentication system implemented for Jarvis AI.

## 🔒 Security Features Implemented

### 1. **Secure Password Management**
- **bcrypt hashing**: Replaced SHA256 with industry-standard bcrypt for password storage
- **Password strength validation**: Enforces strong passwords with complexity requirements
- **Password reset functionality**: Framework for email-based password reset (requires SMTP configuration)

### 2. **User Management & Role-Based Access Control**
- **Database-driven users**: Migrated from hardcoded users to SQLite database
- **Role hierarchy**: admin, moderator, user, guest roles with different permission levels
- **User registration**: New users can register and await admin approval
- **Account management**: Admins can activate/deactivate users and change roles

### 3. **Authentication Security**
- **Rate limiting**: Prevents brute force attacks (5 attempts per 15 minutes)
- **Account locking**: Automatic temporary lock after failed login attempts
- **Session management**: Secure session handling with logout functionality
- **Multi-factor authentication**: Framework ready for 2FA implementation

### 4. **Admin Panel**
- **User management interface**: View, manage, and approve users
- **Pending user approval**: Review and approve new registrations
- **Security monitoring**: View security logs and system events
- **Role management**: Change user roles and permissions

### 5. **Security Logging & Monitoring**
- **Comprehensive logging**: All security events are logged with timestamps
- **Event tracking**: Login attempts, user creation, role changes, etc.
- **Admin visibility**: Security logs accessible through admin panel

### 6. **Database Security**
- **Thread-safe operations**: Database operations protected with locks
- **Error handling**: Graceful fallbacks for database issues
- **Data integrity**: Foreign key constraints and proper data validation

## 🚀 Quick Start

### Prerequisites
```bash
pip install streamlit bcrypt cryptography pyotp qrcode[pil]
```

### Initial Setup
1. **Initialize the database**:
```python
import database
database.init_db()
```

2. **Migrate existing users** (if upgrading):
```bash
python migrate_users.py
```

3. **Run the application**:
```bash
streamlit run app.py
```

## 👥 User Roles

### Admin
- Full system access
- User management capabilities
- View security logs
- Approve pending registrations
- System configuration

### Moderator
- Limited user management
- View basic logs
- Content moderation (when implemented)

### User
- Standard application access
- Personal settings management
- Change own password

### Guest/Demo
- Limited read-only access
- Basic features only

## 🔧 Configuration

### Environment Variables
Create a `.env` file with:
```env
# Email configuration for password reset
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your-email@domain.com
EMAIL_PASSWORD=your-app-password

# Database configuration
DB_NAME=janus_database.db

# Security settings
RATE_LIMIT_ATTEMPTS=5
RATE_LIMIT_WINDOW=15
ACCOUNT_LOCK_DURATION=15
```

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    role TEXT DEFAULT 'user',
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
);
```

### Security Logs Table
```sql
CREATE TABLE security_logs (
    id INTEGER PRIMARY KEY,
    event_type TEXT NOT NULL,
    username TEXT,
    ip_address TEXT,
    user_agent TEXT,
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🔐 API Reference

### Key Functions

#### Authentication
```python
from agent.security import hash_password, verify_password
from database import get_user, update_user_login

# Hash password for storage
hashed = hash_password("user_password")

# Verify password during login
user = get_user("username")
if verify_password("user_password", user["hashed_password"]):
    update_user_login("username", success=True)
```

#### User Management
```python
from database import create_user, get_all_users, update_user_role

# Create new user
create_user("username", "Full Name", "email@domain.com", hashed_password, "user")

# Get all users
users = get_all_users()

# Update user role (admin only)
update_user_role("username", "moderator", "admin_username")
```

#### Security Logging
```python
from database import log_security_event, get_security_logs

# Log security event
log_security_event("LOGIN_FAILED", username="user", details="Invalid password")

# Get recent logs
logs = get_security_logs(limit=50)
```

## 🛡️ Security Best Practices

### For Administrators
1. **Regular monitoring**: Check security logs regularly
2. **User review**: Periodically review user accounts and roles
3. **Password policies**: Enforce strong password requirements
4. **Update management**: Keep dependencies updated

### For Developers
1. **Input validation**: Always validate user input
2. **Error handling**: Implement graceful error handling
3. **Logging**: Log security-relevant events
4. **Testing**: Test authentication flows thoroughly

### For Users
1. **Strong passwords**: Use unique, complex passwords
2. **Enable 2FA**: When available, enable two-factor authentication
3. **Logout**: Always logout when finished
4. **Report issues**: Report suspicious activity to administrators

## 🔄 Migration Guide

### From Hardcoded Authentication
1. Run the migration script: `python migrate_users.py`
2. Update any hardcoded references to use database functions
3. Test all authentication flows
4. Update user documentation

### Database Upgrades
The system automatically creates new tables if they don't exist. For schema changes:
1. Backup existing database
2. Run `database.init_db()` to create new tables
3. Migrate data if necessary
4. Test functionality

## 🚨 Troubleshooting

### Common Issues

#### Database Locked Error
```python
# Solution: Ensure proper connection handling
with _db_lock:
    conn = sqlite3.connect(DB_NAME, timeout=10.0)
    # ... database operations
    conn.close()
```

#### Rate Limiting Too Aggressive
```python
# Adjust rate limiting parameters
is_rate_limited(identifier, max_attempts=10, window_minutes=30)
```

#### Password Reset Not Working
1. Check SMTP configuration in environment variables
2. Verify email credentials
3. Check firewall/network settings

## 📝 Future Enhancements

### Planned Features
- [ ] Email verification for new accounts
- [ ] Advanced 2FA with authenticator apps
- [ ] IP-based access restrictions
- [ ] Advanced session management
- [ ] Audit trail enhancements
- [ ] OAuth integration (Google, GitHub, etc.)
- [ ] Password complexity scoring
- [ ] Automated security reports

### Integration Points
- [ ] LDAP/Active Directory integration
- [ ] Single Sign-On (SSO) support
- [ ] API authentication tokens
- [ ] Webhook notifications for security events

## 📞 Support

For security-related issues or questions:
1. Check this documentation first
2. Review security logs in the admin panel
3. Contact system administrators
4. For critical security issues, follow incident response procedures

---

**Note**: This security system provides enterprise-grade authentication for Jarvis AI. Regular security reviews and updates are recommended to maintain optimal protection.