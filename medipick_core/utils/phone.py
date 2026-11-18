"""Sri Lankan phone normalization, validation, masking, and text hygiene helpers."""
from __future__ import annotations

import re

_INVISIBLE_RE = re.compile(r"[\u200B-\u200F\u202A-\u202E\u2060-\u2069\uFEFF\u00AD]")
_WS_RE = re.compile(r"\s+")
_FULLWIDTH_TRANS = str.maketrans("０１２３４５６７８９＋－（）　", "0123456789+-() ")
_ALLOWED_PHONE_CHARS_RE = re.compile(r"^\+?[\d\s().\-–—−]+$")

SL_MOBILE_RE = re.compile(r"^\+947[01245678]\d{7}$")
SL_PHONE_RE = re.compile(
    r"^\+94(?:7[01245678]|11|2[13-7]|3[1-8]|4[157]|5[12457]|6[35-7]|81|91)\d{7}$"
)


def strip_invisible(value: str) -> str:
    """Remove zero-width / bidi directional marks often pasted from WhatsApp or Contacts."""
    return _INVISIBLE_RE.sub("", value)


def clean_text(value: str) -> str:
    """Strip invisible Unicode controls and collapse internal whitespace."""
    return _WS_RE.sub(" ", strip_invisible(value)).strip()


def clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = clean_text(value)
    return cleaned or None


def normalize_email(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = strip_invisible(value).strip().lower()
    return cleaned or None


def normalize_otp_input(value: str) -> str:
    """Clean pasted 6-digit OTPs (spaces, dashes, zero-width marks)."""
    return re.sub(r"[\s\-]", "", strip_invisible(value).translate(_FULLWIDTH_TRANS))


def parse_sl_phone(raw: str, *, allow_landline: bool = False) -> str:
    """
    Parse messy or pasted Sri Lankan numbers into strict E.164 ('+94XXXXXXXXX').
    Handles '+94 (0) 77-123 4567', '0094771234567', '94771234567', '077 123 4567',
    '771234567', 'tel:+94...', fullwidth digits, and WhatsApp/Contacts bidi chars.
    Raises ValueError on invalid format so Pydantic produces field-level 400 errors.
    """
    text = strip_invisible(raw or "").translate(_FULLWIDTH_TRANS).strip()
    if text.lower().startswith("tel:"):
        text = text[4:].strip()
    if not text:
        raise ValueError("Phone number is required.")

    # Allow "(+94) ..." by checking without a single leading open paren, then verify allowed chars.
    probe = text.lstrip("(").strip()
    has_plus = probe.startswith("+")
    if not _ALLOWED_PHONE_CHARS_RE.match(probe):
        raise ValueError("Enter a valid Sri Lankan mobile number (e.g. +94771234567 or 0771234567).")

    compact = re.sub(r"[\s().\-–—−]", "", text)
    if compact.count("+") > (1 if has_plus else 0) or (has_plus and not compact.startswith("+")):
        raise ValueError("Enter a valid Sri Lankan mobile number (e.g. +94771234567 or 0771234567).")

    digits = compact[1:] if has_plus else compact
    if not digits.isdigit():
        raise ValueError("Phone number contains invalid characters.")

    subscriber: str | None = None
    if has_plus:
        if digits.startswith("94"):
            sub = digits[2:]
            if len(sub) == 10 and sub.startswith("0"):
                sub = sub[1:]
            if len(sub) == 9:
                subscriber = sub
    else:
        if digits.startswith("0094"):
            sub = digits[4:]
            if len(sub) == 10 and sub.startswith("0"):
                sub = sub[1:]
            if len(sub) == 9:
                subscriber = sub
        elif digits.startswith("94") and len(digits) in (11, 12):
            sub = digits[2:]
            if len(sub) == 10 and sub.startswith("0"):
                sub = sub[1:]
            if len(sub) == 9:
                subscriber = sub
        elif digits.startswith("0") and len(digits) == 10:
            subscriber = digits[1:]
        elif len(digits) == 9:
            subscriber = digits

    candidate = f"+94{subscriber}" if subscriber else ""
    pattern = SL_PHONE_RE if allow_landline else SL_MOBILE_RE
    if not pattern.match(candidate):
        hint = "+94771234567 / +94112345678" if allow_landline else "+94771234567 (07X XXX XXXX)"
        raise ValueError(f"Enter a valid Sri Lankan phone number, e.g. {hint}.")
    return candidate


def mask_phone(phone: str | None) -> str:
    if not phone:
        return ""
    return phone[:5] + "*" * max(len(phone) - 7, 0) + phone[-2:] if len(phone) > 7 else phone


def normalize_phone(raw: str, *, allow_landline: bool = False) -> str:
    """Service-layer helper raising MediPickException(400) for invalid numbers."""
    from medipick_core.exceptions import MediPickException
    try:
        return parse_sl_phone(raw, allow_landline=allow_landline)
    except ValueError as exc:
        raise MediPickException("INVALID_PHONE", 400, str(exc)) from exc
