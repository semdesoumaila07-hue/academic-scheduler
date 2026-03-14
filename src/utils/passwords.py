"""Password hashing utilities using PBKDF2 (no extra dependencies).

Provides `hash_password` and `verify_password`.
"""
import os
import hashlib
import binascii

_ALG = 'sha256'
_ITERATIONS = 100_000
_SALT_BYTES = 16


def hash_password(password: str) -> str:
    """Hash a plaintext password and return a string salt$hash_hex."""
    if isinstance(password, str):
        password = password.encode('utf-8')
    salt = os.urandom(_SALT_BYTES)
    dk = hashlib.pbkdf2_hmac(_ALG, password, salt, _ITERATIONS)
    return f"{binascii.hexlify(salt).decode()}${binascii.hexlify(dk).decode()}"


def verify_password(password: str, stored: str) -> bool:
    """Verify a plaintext password against stored salt$hash_hex."""
    try:
        salt_hex, hash_hex = stored.split('$')
    except ValueError:
        return False

    salt = binascii.unhexlify(salt_hex)
    if isinstance(password, str):
        password = password.encode('utf-8')
    dk = hashlib.pbkdf2_hmac(_ALG, password, salt, _ITERATIONS)
    return binascii.hexlify(dk).decode() == hash_hex
