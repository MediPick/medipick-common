"""
MediPick — Custom Exceptions & Error Models
Unified exception class matching standard API error envelope.
"""
from __future__ import annotations


class MediPickException(Exception):
    """
    Raise this anywhere in the application to return a structured API error.
    Example:
        raise MediPickException("OTP_INVALID", 400, "The OTP you entered is incorrect.")
    """
    def __init__(self, code: str, status_code: int, message: str, fields: dict[str, str] | None = None) -> None:
        self.code = code
        self.status_code = status_code
        self.message = message
        self.fields = fields
        super().__init__(message)


def error_json(code: str, message: str, status_code: int, fields: dict | None = None) -> dict:
    """Standard MediPick JSON error response payload dictionary."""
    body: dict = {"success": False, "error": code, "message": message, "statusCode": status_code}
    if fields:
        body["fields"] = fields
    return body
