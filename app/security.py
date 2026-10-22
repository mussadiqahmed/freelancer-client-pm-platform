import hashlib
import secrets

# PBKDF2 stays in the standard library so the course app has no crypto dependency.
# 200,000 iterations is slow enough for a student project without a separate KDF package.
_ITERATIONS = 200_000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _ITERATIONS)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    salt, separator, digest = stored.partition("$")
    if not separator or not salt or not digest:
        return False
    check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _ITERATIONS)
    return secrets.compare_digest(check.hex(), digest)


def new_csrf_token() -> str:
    return secrets.token_urlsafe(32)
