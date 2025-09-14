"""
Utility functions for password hashing, OTP generation, and validation.
"""
import bcrypt
import secrets
import string
from datetime import datetime, timedelta
from typing import Tuple

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password: Plain text password
        hashed: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False

def generate_otp() -> str:
    """
    Generate a 6-digit OTP.
    
    Returns:
        6-digit OTP string
    """
    return ''.join(secrets.choice(string.digits) for _ in range(6))

def hash_otp(otp: str) -> str:
    """
    Hash an OTP for secure storage.
    
    Args:
        otp: Plain text OTP
        
    Returns:
        Hashed OTP string
    """
    return hash_password(otp)

def verify_otp(otp: str, hashed: str) -> bool:
    """
    Verify an OTP against its hash.
    
    Args:
        otp: Plain text OTP
        hashed: Hashed OTP from database
        
    Returns:
        True if OTP matches, False otherwise
    """
    return verify_password(otp, hashed)

def generate_otp_with_expiry(minutes: int = 10) -> Tuple[str, str, datetime]:
    """
    Generate an OTP with expiry time.
    
    Args:
        minutes: Expiry time in minutes (default 10)
        
    Returns:
        Tuple of (plain_otp, hashed_otp, expiry_datetime)
    """
    otp = generate_otp()
    hashed = hash_otp(otp)
    expiry = datetime.utcnow() + timedelta(minutes=minutes)
    
    return otp, hashed, expiry

def is_otp_expired(expiry_time: datetime) -> bool:
    """
    Check if an OTP has expired.
    
    Args:
        expiry_time: OTP expiry datetime
        
    Returns:
        True if expired, False otherwise
    """
    return datetime.utcnow() > expiry_time

def validate_email(email: str) -> bool:
    """
    Basic email validation.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    return True, ""