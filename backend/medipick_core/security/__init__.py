"""
MediPick Core — Security & Cryptographic Utilities
JWT creation/verification, OTP generation/hashing, refresh token hashing.
"""
from __future__ import annotations

import hashlib
import os
import secrets
import string
import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

DEFAULT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
DEFAULT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))

# ─── Password / OTP Context ───────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─── OTP ─────────────────────────────────────────────────────────────────────

def generate_otp() -> str:
    """Returns a cryptographically random 6-digit OTP string."""
    return "".join(secrets.choice(string.digits) for _ in range(6))


def hash_otp(otp: str) -> str:
    """bcrypt-hash the OTP for storage."""
    return pwd_context.hash(otp)


def verify_otp_hash(plain_otp: str, hashed_otp: str) -> bool:
    """Verify a plain OTP against its stored bcrypt hash."""
    return pwd_context.verify(plain_otp, hashed_otp)


# ─── Refresh Token ────────────────────────────────────────────────────────────

def generate_refresh_token() -> str:
    """Returns a new opaque UUID4 refresh token (raw, un-hashed)."""
    return str(uuid.uuid4())


def hash_refresh_token(raw_token: str) -> str:
    """SHA-256 hex digest of the raw refresh token for DB storage."""
    return hashlib.sha256(raw_token.encode()).hexdigest()


# ─── JWT Access Token ─────────────────────────────────────────────────────────

def create_access_token(
    user_id: str,
    phone_number: str,
    role: str = "CUSTOMER",
    scope: str = "full",
    expires_minutes: int | None = None,
    secret_key: str | None = None,
    algorithm: str | None = None,
) -> str:
    """
    Creates a signed JWT access token.
    Payload: { sub, role, phone, scope, iat, exp }
    """
    now = datetime.now(timezone.utc)
    duration = expires_minutes or DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES
    expire = now + timedelta(minutes=duration)

    payload = {
        "sub": str(user_id),
        "role": role,
        "phone": phone_number,
        "scope": scope,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    key = secret_key or DEFAULT_SECRET_KEY
    alg = algorithm or DEFAULT_ALGORITHM
    return jwt.encode(payload, key, algorithm=alg)


def decode_access_token(
    token: str,
    secret_key: str | None = None,
    algorithm: str | None = None,
) -> dict:
    """
    Decodes and verifies a JWT access token.
    Raises jose.JWTError on invalid/expired tokens.
    """
    key = secret_key or DEFAULT_SECRET_KEY
    alg = algorithm or DEFAULT_ALGORITHM
    return jwt.decode(token, key, algorithms=[alg])


# ─── Pharmacy staff tokens ────────────────────────────────────────────────────

def create_staff_access_token(
    user_id: str,
    phone_number: str,
    role: str,
    pharmacy_id: str,
    staff_role: str,
    expires_minutes: int | None = None,
    secret_key: str | None = None,
    algorithm: str | None = None,
) -> str:
    """
    Same claim set as create_access_token, plus `pharmacy_id` and `staff_role`.
    """
    now = datetime.now(timezone.utc)
    duration = expires_minutes or DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES
    payload = {
        "sub": str(user_id),
        "role": role,
        "phone": phone_number,
        "scope": "full",
        "pharmacy_id": str(pharmacy_id),
        "staff_role": staff_role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=duration)).timestamp()),
    }
    key = secret_key or DEFAULT_SECRET_KEY
    alg = algorithm or DEFAULT_ALGORITHM
    return jwt.encode(payload, key, algorithm=alg)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str | None) -> bool:
    if not hashed:
        return False
    try:
        return pwd_context.verify(password, hashed)
    except ValueError:
        return False

__all__ = [
    "generate_otp",
    "hash_otp",
    "verify_otp_hash",
    "generate_refresh_token",
    "hash_refresh_token",
    "create_access_token",
    "create_staff_access_token",
    "decode_access_token",
    "hash_password",
    "verify_password",
    "JWTError",
]
