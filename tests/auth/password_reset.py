"""
Password reset functionality for Jarvis AI
"""

import smtplib
import secrets
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import Optional

import database
from agent.features.security import generate_reset_token, log_security_event

logger = logging.getLogger(__name__)

# Email configuration (these should be environment variables in production)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "your-jarvis-ai@gmail.com"  # Replace with actual email
EMAIL_PASSWORD = "your-app-password"  # Replace with actual app password

def send_reset_email(email: str, username: str, reset_token: str) -> bool:
    """Send password reset email to user"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = email
        msg['Subject'] = "Jarvis AI - Password Reset"
        
        # Email body
        body = f"""
        Hello {username},
        
        You have requested a password reset for your Jarvis AI account.
        
        Click the link below to reset your password:
        http://localhost:8501/reset-password?token={reset_token}
        
        This link will expire in 1 hour.
        
        If you did not request this password reset, please ignore this email.
        
        Best regards,
        The Jarvis AI Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to server and send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, email, text)
        server.quit()
        
        logger.info(f"Password reset email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send reset email to {email}: {e}")
        return False

def request_password_reset(email: str) -> tuple[bool, str]:
    """Request password reset for user by email"""
    # Find user by email
    conn = database.sqlite3.connect(database.DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE email = ? AND is_active = 1", (email,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        # Don't reveal if email exists for security
        return True, "If your email is registered, you will receive a reset link shortly."
    
    username = result[0]
    
    # Generate reset token
    reset_token = generate_reset_token()
    expires_at = datetime.now() + timedelta(hours=1)
    
    # Save token to database
    database.set_password_reset_token(username, reset_token, expires_at)
    
    # Send email
    user = database.get_user(username)
    if user and send_reset_email(user["email"], username, reset_token):
        log_security_event("PASSWORD_RESET_REQUESTED", username=username, details=f"Reset email sent to {email}")
        return True, "If your email is registered, you will receive a reset link shortly."
    else:
        return False, "Failed to send reset email. Please try again later."

def reset_password_with_token(token: str, new_password: str) -> tuple[bool, str]:
    """Reset password using valid token"""
    from agent.features.security import hash_password, validate_password_strength
    
    # Validate new password
    is_strong, message = validate_password_strength(new_password)
    if not is_strong:
        return False, f"Password requirements: {message}"
    
    # Verify token
    username = database.verify_reset_token(token)
    if not username:
        return False, "Invalid or expired reset token."
    
    # Hash new password and update
    hashed_password = hash_password(new_password)
    database.update_user_password(username, hashed_password)
    
    log_security_event("PASSWORD_RESET_COMPLETED", username=username)
    return True, "Password has been reset successfully. You can now log in with your new password."

def send_verification_email(email: str, username: str, verification_token: str) -> bool:
    """Send email verification to new user"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = email
        msg['Subject'] = "Jarvis AI - Verify Your Email"
        
        # Email body
        body = f"""
        Hello {username},
        
        Welcome to Jarvis AI! Please verify your email address by clicking the link below:
        
        http://localhost:8501/verify-email?token={verification_token}
        
        This link will expire in 24 hours.
        
        If you did not create this account, please ignore this email.
        
        Best regards,
        The Jarvis AI Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to server and send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, email, text)
        server.quit()
        
        logger.info(f"Verification email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {email}: {e}")
        return False