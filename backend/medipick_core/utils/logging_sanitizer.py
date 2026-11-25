"""
MediPick — Server Log Sanitizer
Redacts credentials, tokens, OTPs, PINs, Authorization headers, and sensitive PII from server logs.
"""
from __future__ import annotations

import logging
import re

_SENSITIVE_PATTERNS = [
    (re.compile(r"(Bearer\s+)[A-Za-z0-9\-_.~+/]+=*", re.IGNORECASE), r"\1[REDACTED_TOKEN]"),
    (
        re.compile(
            r'(["\']?(?:password|current_password|new_password|secret|pwd)["\']?\s*[:=]\s*["\']?)([^"\',\s&]{1,100})(["\']?)',
            re.IGNORECASE,
        ),
        r"\1[REDACTED_PASSWORD]\3",
    ),
    (
        re.compile(
            r'(["\']?(?:otp|code|pin|pickupCode)["\']?\s*[:=]\s*["\']?)\b(\d{4,8})\b(["\']?)',
            re.IGNORECASE,
        ),
        r"\1[REDACTED_CODE]\3",
    ),
    (
        re.compile(
            r'(["\']?(?:access_token|refresh_token|accessToken|refreshToken|token)["\']?\s*[:=]\s*["\']?)ey[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+(["\']?)',
            re.IGNORECASE,
        ),
        r"\1[REDACTED_JWT]\2",
    ),
    (
        re.compile(
            r'(["\']?(?:account_number|card_number|accountNumber|cardNumber|cvv)["\']?\s*[:=]\s*["\']?)\b(\d{6,20})\b(["\']?)',
            re.IGNORECASE,
        ),
        r"\1[REDACTED_ACCOUNT]\3",
    ),
]


class SensitiveDataFilter(logging.Filter):
    """Logging filter that redacts sensitive credentials and PII from all log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for pattern, repl in _SENSITIVE_PATTERNS:
                record.msg = pattern.sub(repl, record.msg)

        if record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: self._sanitize_value(v) for k, v in record.args.items()
                }
            elif isinstance(record.args, (list, tuple)):
                record.args = tuple(self._sanitize_value(v) for v in record.args)

        return True

    @staticmethod
    def _sanitize_value(val: object) -> object:
        if isinstance(val, str):
            for pattern, repl in _SENSITIVE_PATTERNS:
                val = pattern.sub(repl, val)
        return val


def setup_log_sanitization() -> None:
    """Attaches SensitiveDataFilter to all active handlers on root and uvicorn loggers."""
    log_filter = SensitiveDataFilter()
    root_logger = logging.getLogger()
    root_logger.addFilter(log_filter)
    for handler in root_logger.handlers:
        handler.addFilter(log_filter)

    for name in ("uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"):
        l = logging.getLogger(name)
        l.addFilter(log_filter)
        for handler in l.handlers:
            handler.addFilter(log_filter)


__all__ = ["SensitiveDataFilter", "setup_log_sanitization"]

