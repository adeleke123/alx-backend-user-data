#!/usr/bin/env python3
"""
Encrypting and Checking valid password
"""
import bcrypt


def hash_password(password: str) -> bytes:
    """
    Hashes the provided password using bcrypt.
    Args:
        password: The password to hash.
    Returns:
        The hashed password as a byte string.
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password


def is_valid(hashed_password: bytes, password: str) -> bool:
    """
    Validates if the provided password matches the hashed password.
    Args:
        hashed_password: The hashed password as a byte string.
        password: The password to check.
    Returns:
        True - password matches the hashed password, otherwise False
    """
    return bcrypt.checkpw(password.encode(), hashed_password)
