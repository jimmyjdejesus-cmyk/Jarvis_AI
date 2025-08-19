"""
Two-Factor Authentication (2FA) module for Jarvis AI
Simple TOTP implementation
"""

import io
import base64
from datetime import datetime
import database.database as database

# Mock implementations for dependencies that might be missing
try:
    import pyotp
    import qrcode
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    # Create stub implementation
    class PyotpStub:
        def random_base32(self):
            return "MOCKBASE32SECRET"
            
        class totp:
            class TOTP:
                def __init__(self, secret):
                    self.secret = secret
                    
                def provisioning_uri(self, name, issuer_name):
                    return f"otpauth://totp/{issuer_name}:{name}?secret={self.secret}&issuer={issuer_name}"
                    
                def verify(self, code):
                    return code == "123456"  # Mock verification that accepts "123456"
    
    pyotp = PyotpStub()

from agent.features.security import log_security_event

def generate_2fa_secret(username: str) -> str:
    """Generate a new 2FA secret for user"""
    if not MODULES_AVAILABLE:
        log_security_event("2FA_MODULES_UNAVAILABLE", username=username)
        return None
        
    secret = pyotp.random_base32()
    
    # Store in database
    database.update_user_field(username, "two_fa_secret", secret)
    
    return secret

def get_2fa_qr_code(username: str, secret: str) -> str:
    """Generate QR code for 2FA setup"""
    if not MODULES_AVAILABLE:
        log_security_event("2FA_MODULES_UNAVAILABLE", username=username)
        return None
        
    # Create TOTP URI
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=username,
        issuer_name="Jarvis AI"
    )
    
    # Generate QR code
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for display in browser
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return img_str
    except Exception as e:
        log_security_event("2FA_QR_GENERATION_FAILED", username=username, details=str(e))
        return None

def is_2fa_enabled(username: str) -> bool:
    """Check if 2FA is enabled for a user"""
    user = database.get_user(username)
    if not user:
        return False
        
    return user.get("two_fa_enabled", False) and user.get("two_fa_secret") is not None

def verify_2fa_code(username: str, code: str) -> bool:
    """Verify a 2FA code"""
    if not MODULES_AVAILABLE:
        log_security_event("2FA_MODULES_UNAVAILABLE", username=username)
        return False
        
    user = database.get_user(username)
    if not user or not user.get("two_fa_secret"):
        log_security_event("2FA_VERIFY_NO_SECRET", username=username)
        return False
        
    secret = user.get("two_fa_secret")
    totp = pyotp.totp.TOTP(secret)
    
    # Verify code
    is_valid = totp.verify(code)
    
    if not is_valid:
        log_security_event("2FA_CODE_INVALID", username=username)
    
    return is_valid

def enable_2fa(username: str) -> dict:
    """Enable 2FA for a user. Returns secret for setup"""
    if not MODULES_AVAILABLE:
        return {"status": "error", "message": "2FA modules not available"}
        
    # Generate secret
    secret = generate_2fa_secret(username)
    
    if not secret:
        return {"status": "error", "message": "Failed to generate 2FA secret"}
    
    # Set as pending until verified with setup code
    database.update_user_field(username, "two_fa_pending", True)
    
    # Generate QR code
    qr_code = get_2fa_qr_code(username, secret)
    
    log_security_event("2FA_SETUP_INITIATED", username=username)
    
    return {
        "status": "success",
        "secret": secret,
        "qr_code": qr_code
    }

def disable_2fa(username: str) -> dict:
    """Disable 2FA for a user"""
    database.update_user_field(username, "two_fa_enabled", False)
    database.update_user_field(username, "two_fa_pending", False)
    database.update_user_field(username, "two_fa_secret", None)
    
    log_security_event("2FA_DISABLED", username=username)
    
    return {
        "status": "success", 
        "message": "Two-factor authentication has been disabled"
    }
