"""
MediPick Core — Input Sanitization & XSS Prevention Utilities
Strips HTML tags, script blocks, dangerous control characters, and bidi overrides.
"""
from __future__ import annotations

import re
from medipick_core.utils.phone import strip_invisible

_SCRIPT_BLOCK_RE = re.compile(
    r"<(script|style|iframe|object|embed|applet|form|svg|math)[^>]*>.*?</\1>",
    re.IGNORECASE | re.DOTALL,
)
_HTML_TAG_RE = re.compile(r"<[^>]+>")
_DANGEROUS_ASCII_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_WS_RE = re.compile(r"\s+")


def sanitize_html(text: str | None) -> str:
    """
    Sanitize text input by removing all HTML tags, executable script blocks,
    dangerous ASCII control characters, and zero-width/bidi override characters.
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)

    # 1. Strip dangerous tags with their contents (script, style, iframe, etc.)
    cleaned = _SCRIPT_BLOCK_RE.sub("", text)
    # 2. Strip any remaining HTML tags
    cleaned = _HTML_TAG_RE.sub("", cleaned)
    # 3. Strip non-printable ASCII control characters (preserving newline & tab)
    cleaned = _DANGEROUS_ASCII_CTRL.sub("", cleaned)
    # 4. Strip zero-width and bidi override characters
    cleaned = strip_invisible(cleaned)
    return cleaned.strip()


def sanitize_text(text: str | None, max_length: int | None = None) -> str:
    """
    Cleans text, collapses whitespace, strips HTML, and optionally enforces max_length.
    """
    cleaned = sanitize_html(text)
    collapsed = _WS_RE.sub(" ", cleaned).strip()
    if max_length and len(collapsed) > max_length:
        return collapsed[:max_length].strip()
    return collapsed


def mask_phone_number(phone: str | None) -> str:
    """
    Mask phone number for safe display and logging (e.g. +94 77 123 4567 -> +94 77 *** *567).
    """
    if not phone:
        return ""
    digits = re.sub(r"\D", "", phone)
    if len(digits) >= 9:
        return f"{phone[:6]}***{phone[-4:]}"
    return "***"
