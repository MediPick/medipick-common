"""
MediPick Core — Shared Text, License, Banking, Promo, and Date Validators.
"""
from __future__ import annotations

import re
from datetime import date

from medipick_core.utils.phone import strip_invisible
from medipick_core.utils.sanitizer import sanitize_html
from medipick_core.utils.timeutil import LOCAL_TZ, utcnow

_WS_RE = re.compile(r"\s+")
_FULLWIDTH_DIGITS = str.maketrans("０１２３４５６７８９", "0123456789")
_SLMC_RE = re.compile(r"^(?=.*\d)[A-Z0-9][A-Z0-9/.\-\s]{2,28}[A-Z0-9]$")
_NMRA_RE = re.compile(r"^(?=.*\d)[A-Z0-9][A-Z0-9/.\-\s]{3,38}[A-Z0-9]$")
_PROMO_CODE_RE = re.compile(r"^[A-Z0-9_-]{3,40}$")
_BANK_ACCOUNT_RE = re.compile(r"^\d{6,20}$")
_CLOCK_TIME_RE = re.compile(r"^(?:(?:0?[1-9]|1[0-2]):[0-5]\d\s?(?:AM|PM)|(?:[01]?\d|2[0-3]):[0-5]\d)$", re.IGNORECASE)


def clean_text(value: str) -> str:
    """Strip HTML, dangerous control characters, invisible chars and collapse whitespace."""
    sanitized = sanitize_html(value)
    return _WS_RE.sub(" ", sanitized).strip()


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
    return re.sub(r"[\s\-]", "", strip_invisible(value).translate(_FULLWIDTH_DIGITS))


def normalize_slmc(value: str) -> str:
    cleaned = clean_text(value).upper()
    if not _SLMC_RE.match(cleaned):
        raise ValueError("Enter a valid SLMC registration number (e.g. SLMC-PH-4412).")
    return cleaned


def normalize_nmra(value: str) -> str:
    cleaned = clean_text(value).upper()
    if not _NMRA_RE.match(cleaned):
        raise ValueError("Enter a valid NMRA licence or registration number (e.g. NMRA-PH-2024-9988).")
    return cleaned


def normalize_bank_account(value: str) -> str:
    digits = re.sub(r"[\s\-]", "", strip_invisible(value).translate(_FULLWIDTH_DIGITS))
    if not _BANK_ACCOUNT_RE.match(digits):
        raise ValueError("Account number must be 6 to 20 digits.")
    return digits


def normalize_promo_code(value: str) -> str:
    code = re.sub(r"\s+", "", strip_invisible(value)).upper()
    if not _PROMO_CODE_RE.match(code):
        raise ValueError("Promo code must be 3-40 letters, numbers, '-' or '_'.")
    return code


def ensure_non_blank_password(value: str, *, min_len: int = 8) -> str:
    cleaned = strip_invisible(value)
    trimmed = cleaned.strip()
    if len(trimmed) < min_len:
        raise ValueError(f"Password must contain at least {min_len} non-space characters.")
    if not any(ch.isalpha() for ch in trimmed) or not any(ch.isdigit() for ch in trimmed):
        raise ValueError("Password must include at least one letter and one number.")
    return cleaned


def clean_upload_filename(value: str) -> str:
    name = clean_text(value)
    if not name or "/" in name or "\\" in name or ".." in name:
        raise ValueError("Enter a valid filename without path characters.")
    return name


def validate_weekly_hours(hours: list[dict] | None) -> list[dict] | None:
    if hours is None:
        return None
    cleaned: list[dict] = []
    for entry in hours:
        if not isinstance(entry, dict):
            raise ValueError("Each schedule entry must be an object.")
        is_open = bool(entry.get("isOpen", True))
        is_24h = bool(entry.get("is24Hours", False))
        open_t = clean_text(str(entry.get("openTime") or ""))
        close_t = clean_text(str(entry.get("closeTime") or ""))
        if is_open and not is_24h:
            if not _CLOCK_TIME_RE.match(open_t) or not _CLOCK_TIME_RE.match(close_t):
                day = entry.get("dayName") or "day"
                raise ValueError(f"Invalid opening/closing time for {day} (use e.g. 08:00 AM).")
            if open_t.upper() == close_t.upper():
                day = entry.get("dayName") or "day"
                raise ValueError(f"Opening and closing time cannot be identical for {day}.")
        cleaned.append({**entry, "openTime": open_t, "closeTime": close_t})
    return cleaned


def ensure_future_or_today(d: date | None, *, label: str = "Date") -> date | None:
    if d is not None and d < utcnow().astimezone(LOCAL_TZ).date():
        raise ValueError(f"{label} cannot be in the past.")
    return d
