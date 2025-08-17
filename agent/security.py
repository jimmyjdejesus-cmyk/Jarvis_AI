import os
from cryptography.fernet import Fernet
import hashlib
import base64

def load_user_key(key_path):
    if os.path.exists(key_path):
        with open(key_path, "rb") as f:
            return f.read()
    key = Fernet.generate_key()
    with open(key_path, "wb") as f:
        f.write(key)
    return key

def encrypt_json(data, key):
    f = Fernet(key)
    import json
    raw = json.dumps(data).encode()
    return f.encrypt(raw)

def decrypt_json(enc, key):
    f = Fernet(key)
    import json
    raw = f.decrypt(enc)
    return json.loads(raw)

def hash_password(password):
    # Hash password for storage (use bcrypt/scrypt for production!)
    return base64.b64encode(hashlib.sha256(password.encode()).digest()).decode()

def verify_password(password, hashed):
    return hash_password(password) == hashed