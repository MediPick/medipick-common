"""MediPick — time helpers."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

DEFAULT_UTC_OFFSET_MINUTES = 330  # Sri Lanka (UTC +05:30)
LOCAL_TZ = timezone(timedelta(minutes=DEFAULT_UTC_OFFSET_MINUTES))


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def as_aware(dt: datetime) -> datetime:
    """DB drivers can hand back naive datetimes; treat those as UTC."""
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def format_local_clock(dt: datetime, tz_offset_minutes: int | None = None) -> str:
    """e.g. "2:15 PM" in local timezone (Sri Lanka by default)."""
    tz = timezone(timedelta(minutes=tz_offset_minutes)) if tz_offset_minutes is not None else LOCAL_TZ
    return as_aware(dt).astimezone(tz).strftime("%I:%M %p").lstrip("0")


__all__ = ["DEFAULT_UTC_OFFSET_MINUTES", "LOCAL_TZ", "utcnow", "as_aware", "format_local_clock"]

