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

import database.database as database
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
        msg['Subject'] = "Jarvis AI Password Reset"
        
        # Email body
        body = f"""
        Hello {username},
        
        We received a request to reset your Jarvis AI password. To reset your password, use the following token:
        
        {reset_token}
        
        If you did not request this password reset, please ignore this email.
        
        This token will expire in 1 hour.
        
        Regards,
        The Jarvis AI Team
        """
        
        # Attach body to email
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to server and send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, email, text)
        server.quit()
        
        return True
    
    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")
        return False


def request_password_reset(username: str) -> dict:
    """
    Request a password reset for the specified user.
    Returns a dictionary with status and message.
    """
    # Get user from database
    user = database.get_user(username)
    
    if not user:
        log_security_event("RESET_REQUEST_NONEXISTENT_USER", username=username)
        # Return success even if user doesn't exist to prevent user enumeration
        return {"status": "success", "message": "If a user with that username exists, a reset email has been sent."}
    
    # Check if user has an email
    email = user.get("email")
    if not email:
        log_security_event("RESET_REQUEST_NO_EMAIL", username=username)
        return {"status": "error", "message": "This account does not have an email address. Contact admin."}
    
    # Generate reset token
    reset_token = generate_reset_token()
    
    # Store token in database with expiration
    expiration = datetime.now() + timedelta(hours=1)
    
    database.store_reset_token(username, reset_token, expiration)
    
    # Send email with reset token
    if send_reset_email(email, username, reset_token):
        log_security_event("PASSWORD_RESET_REQUESTED", username=username)
        return {"status": "success", "message": "Password reset email sent."}
    else:
        log_security_event("PASSWORD_RESET_EMAIL_FAILED", username=username)
        return {"status": "error", "message": "Failed to send reset email. Please try again later."}


def verify_reset_token(username: str, token: str) -> bool:
    """Verify that a reset token is valid for the user"""
    token_data = database.get_reset_token(username)
    
    if not token_data:
        log_security_event("INVALID_RESET_TOKEN", username=username)
        return False
    
    stored_token = token_data.get("token")
    expiration = token_data.get("expiration")
    
    # Check if token matches and is not expired
    if stored_token == token and datetime.now() < datetime.fromisoformat(expiration):
        return True
    
    log_security_event("EXPIRED_RESET_TOKEN" if stored_token == token else "INVALID_RESET_TOKEN", username=username)
    return False


def reset_password(username: str, token: str, new_password: str) -> dict:
    """
    Reset user's password if the token is valid
    Returns a dictionary with status and message
    """
    from agent.features.security import hash_password, validate_password_strength
    
    # Verify reset token
    if not verify_reset_token(username, token):
        return {"status": "error", "message": "Invalid or expired reset token."}
    
    # Validate password strength
    password_check = validate_password_strength(new_password)
    if not password_check["valid"]:
        return {"status": "error", "message": password_check["message"]}
    
    # Hash the new password
    hashed_password = hash_password(new_password)
    
    # Update the password in the database
    if database.update_password(username, hashed_password):
        # Invalidate the used token
        database.invalidate_reset_token(username)
        
        log_security_event("PASSWORD_RESET_SUCCESSFUL", username=username)
        return {"status": "success", "message": "Password has been reset. You can now log in."}
    else:
        log_security_event("PASSWORD_RESET_FAILED", username=username)
        return {"status": "error", "message": "Failed to reset password. Please try again."}
