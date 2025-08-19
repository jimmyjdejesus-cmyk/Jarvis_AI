"""
Two-Factor Authentication (2FA) module for Jarvis AI
Simple TOTP implementation
"""

import pyotp
import qrcode
import io
import base64
from datetime import datetime
import database
from agent.features.security import log_security_event

def generate_2fa_secret(username: str) -> str:
    """Generate a new 2FA secret for user"""
    secret = pyotp.random_base32()
    
    # Save to database
    conn = database.sqlite3.connect(database.DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET two_fa_secret = ? WHERE username = ?", (secret, username))
    conn.commit()
    conn.close()
    
    return secret

def get_2fa_qr_code(username: str, secret: str) -> str:
    """Generate QR code for 2FA setup"""
    # Create TOTP URI
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=username,
        issuer_name="Jarvis AI"
    )
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)
    
    # Convert to base64 image
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

def verify_2fa_token(username: str, token: str) -> bool:
    """Verify 2FA token"""
    user = database.get_user(username)
    if not user or not user["two_fa_enabled"] or not user.get("two_fa_secret"):
        return False
    
    # Verify TOTP token
    totp = pyotp.TOTP(user["two_fa_secret"])
    
    # Allow for some time drift (±1 period)
    is_valid = totp.verify(token, valid_window=1)
    
    if is_valid:
        log_security_event("2FA_SUCCESS", username=username)
    else:
        log_security_event("2FA_FAILED", username=username)
    
    return is_valid

def enable_2fa(username: str, verification_token: str) -> bool:
    """Enable 2FA after user verifies they can generate tokens"""
    if verify_2fa_token(username, verification_token):
        conn = database.sqlite3.connect(database.DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET two_fa_enabled = 1 WHERE username = ?", (username,))
        conn.commit()
        conn.close()
        
        log_security_event("2FA_ENABLED", username=username)
        return True
    return False

def disable_2fa(username: str) -> bool:
    """Disable 2FA for user"""
    conn = database.sqlite3.connect(database.DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET two_fa_enabled = 0, two_fa_secret = NULL WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    
    log_security_event("2FA_DISABLED", username=username)
    return True

def is_2fa_enabled(username: str) -> bool:
    """Check if 2FA is enabled for user"""
    user = database.get_user(username)
    return user and user.get("two_fa_enabled", False)