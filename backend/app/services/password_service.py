import hashlib
import hmac
import os
from typing import Optional


ALGORITHM_NAME = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 600_000
SALT_BYTES = 16


def is_password_hash(value: Optional[str]) -> bool:
    """Return True when value uses the OmniLink PBKDF2 hash format."""
    if not value or not isinstance(value, str):
        return False

    parts = value.split("$")
    if len(parts) != 4:
        return False

    algorithm, iterations, salt_hex, digest_hex = parts

    if algorithm != ALGORITHM_NAME:
        return False

    try:
        int(iterations)
        bytes.fromhex(salt_hex)
        bytes.fromhex(digest_hex)
    except (TypeError, ValueError):
        return False

    return True


def hash_password(password: str) -> str:
    """Create a salted PBKDF2-SHA256 password hash."""
    if not isinstance(password, str) or not password:
        raise ValueError("Password cannot be empty")

    salt = os.urandom(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )

    return "$".join(
        [
            ALGORITHM_NAME,
            str(PBKDF2_ITERATIONS),
            salt.hex(),
            digest.hex(),
        ]
    )


def verify_password(password: str, stored_value: str) -> bool:
    """
    Verify a password against an OmniLink PBKDF2 hash.

    Plaintext is intentionally not accepted here. Compatibility migration
    is handled explicitly by auth.py so it can immediately replace the
    old value after one successful login.
    """
    if not password or not is_password_hash(stored_value):
        return False

    algorithm, iterations, salt_hex, digest_hex = stored_value.split("$")
    expected_digest = bytes.fromhex(digest_hex)
    calculated_digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt_hex),
        int(iterations),
    )

    return hmac.compare_digest(calculated_digest, expected_digest)


def plaintext_matches(password: str, stored_value: str) -> bool:
    """Constant-time comparison used only during legacy migration."""
    if stored_value is None:
        return False
    return hmac.compare_digest(
        str(password).encode("utf-8"),
        str(stored_value).encode("utf-8"),
    )
