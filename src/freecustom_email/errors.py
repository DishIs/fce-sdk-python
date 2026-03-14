"""
Errors — FreeCustom.Email Python SDK
All exceptions inherit from FreecustomEmailError so callers can catch them broadly.
"""
from __future__ import annotations
from typing import Optional


class FreecustomEmailError(Exception):
    """Base exception for all FreeCustom.Email SDK errors."""

    def __init__(
        self,
        message: str,
        *,
        status: Optional[int] = None,
        code: Optional[str] = None,
        hint: Optional[str] = None,
        upgrade_url: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.hint = hint
        self.upgrade_url = upgrade_url

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={str(self)!r}, "
            f"status={self.status}, "
            f"code={self.code!r})"
        )


class AuthError(FreecustomEmailError):
    """Raised when the API key is missing, invalid, or revoked."""
    def __init__(self, message: str = "Invalid or missing API key") -> None:
        super().__init__(message, status=401, code="unauthorized")


class PlanError(FreecustomEmailError):
    """Raised when the operation requires a higher plan tier."""
    def __init__(self, message: str, upgrade_url: Optional[str] = None) -> None:
        super().__init__(message, status=403, code="plan_required", upgrade_url=upgrade_url)


class RateLimitError(FreecustomEmailError):
    """Raised when a rate limit (per-second or monthly) is exceeded."""
    def __init__(self, message: str, retry_after: Optional[int] = None) -> None:
        super().__init__(message, status=429, code="rate_limit_exceeded")
        self.retry_after = retry_after


class NotFoundError(FreecustomEmailError):
    """Raised when the requested resource does not exist."""
    def __init__(self, message: str) -> None:
        super().__init__(message, status=404, code="not_found")


class TimeoutError(FreecustomEmailError):
    """Raised when a request exceeds the configured timeout."""
    def __init__(self, timeout_ms: int) -> None:
        super().__init__(f"Request timed out after {timeout_ms}ms")
        self.timeout_ms = timeout_ms


class WaitTimeoutError(FreecustomEmailError):
    """Raised when wait_for() or otp.wait_for() times out."""
    def __init__(self, inbox: str, timeout_ms: int) -> None:
        super().__init__(
            f"Timed out waiting for {inbox} after {timeout_ms}ms",
            code="wait_timeout",
        )
        self.inbox = inbox
        self.timeout_ms = timeout_ms
