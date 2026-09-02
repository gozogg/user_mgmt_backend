import hashlib
import hmac
import os

PBKDF2_ITERATIONS = 100_000


def hash_password(password, salt=None):
    """Return salt:hex using PBKDF2-SHA256. Stdlib only so Lambda packages stay simple."""
    if not password:
        raise ValueError("password is required")
    salt_bytes = salt or os.urandom(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_bytes,
        PBKDF2_ITERATIONS,
    )
    return f"{salt_bytes.hex()}:{derived.hex()}"


def verify_password(password, stored):
    if not password or not stored or ":" not in stored:
        return False
    salt_hex, hash_hex = stored.split(":", 1)
    try:
        salt_bytes = bytes.fromhex(salt_hex)
    except ValueError:
        return False
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_bytes,
        PBKDF2_ITERATIONS,
    )
    return hmac.compare_digest(derived.hex(), hash_hex)
