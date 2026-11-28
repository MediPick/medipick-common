"""
MediPick Core — Shared Storage Rules, Key Parsers, and Signature Verification.
"""
from __future__ import annotations

import hashlib
import hmac
import re
import time
import uuid

# purpose/<user uuid>/<random hex> — strict so a key can never escape UPLOAD_DIR.
_FILE_KEY_RE = re.compile(r"^[a-z_]+/[0-9a-f-]{36}/[0-9a-f]{32}$")

# ── Infrastructure Cost Protection & DoS Guardrails ───────────────────────────
MAX_UPLOAD_BYTES: int = 10 * 1024 * 1024      # 10 MB hard payload ceiling (prevents RAM saturation)
MAX_IMAGE_PIXELS: int = 25_000_000             # 25 Megapixels (prevents Decompression Bomb DoS)
MAX_PRESCRIPTION_PAGES: int = 5                # Max prescription pages per order (prevents page flooding)
PRESIGNED_URL_TTL_SECONDS: int = 900           # 15-minute temporary presigned URL expiration
CLARITY_THRESHOLD_SCORE: int = 50              # Fail-fast clarity threshold (skips expensive YOLO inference)

ALLOWED_CONTENT_TYPES: set[str] = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif",
    "application/pdf",
}


def make_file_key(purpose: str, owner_user_id: uuid.UUID) -> str:
    """Generate a structured, non-guessable storage file key."""
    return f"{purpose}/{owner_user_id}/{uuid.uuid4().hex}"


def is_valid_file_key(file_key: str) -> bool:
    """Validate format: purpose/<user-uuid>/<32-hex-chars>."""
    return bool(_FILE_KEY_RE.match(file_key))


def owner_id_from_key(file_key: str) -> str:
    """Extract owner UUID string from a valid file key."""
    return file_key.split("/")[1]


def is_owned_file_key(
    file_key: str,
    owner_user_id: uuid.UUID,
    allowed_prefixes: tuple[str, ...] | None = None,
) -> bool:
    """Validate file key format, prefix (purpose), and ownership."""
    if not is_valid_file_key(file_key):
        return False
    prefix = file_key.split("/")[0]
    if allowed_prefixes is not None and prefix not in allowed_prefixes:
        return False
    return owner_id_from_key(file_key) == str(owner_user_id)


def detect_content_type(data: bytes) -> str | None:
    """Sniff the real file type from magic bytes — never trust client Content-Type."""
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    if data.startswith(b"%PDF"):
        return "application/pdf"
    if len(data) >= 12 and data[4:8] == b"ftyp":
        brand = data[8:12]
        if brand in (b"heic", b"heix", b"heim", b"heis", b"mif1", b"msf1"):
            return "image/heic"
    return None


def make_storage_signature(action: str, file_key: str, expires: int, secret_key: str) -> str:
    """Generate HMAC SHA-256 signature for signed URL authorization."""
    message = f"{action}:{file_key}:{expires}".encode()
    return hmac.new(secret_key.encode(), message, hashlib.sha256).hexdigest()


def verify_storage_signature(
    action: str, file_key: str, expires: int, signature: str, secret_key: str
) -> bool:
    """Verify HMAC signature and check that it has not expired."""
    now = int(time.time())
    if expires < now or expires > now + 7200:
        return False
    expected = make_storage_signature(action, file_key, expires, secret_key)
    return hmac.compare_digest(expected, signature)
