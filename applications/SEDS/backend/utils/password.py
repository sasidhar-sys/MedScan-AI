"""
MedScan AI
Smart Esophageal Diagnosis System (SEDS)
Password Security Utilities

Author: Sasidhar A
"""

import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    Truncates to 72 bytes as per bcrypt specification.
    """
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a hashed password.
    """
    pwd_bytes = plain_password.encode("utf-8")[:72]
    hash_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(pwd_bytes, hash_bytes)
