"""
HTTP client — FreeCustom.Email Python SDK
Built on httpx for async-first usage with sync fallback via httpx.Client.
Handles: auth, timeout, retry with backoff, error mapping.
"""
from __future__ import annotations

import asyncio
import json
from typing import Any, Optional

import httpx

from .errors import (
    FreecustomEmailError,
    AuthError,
    PlanError,
    RateLimitError,
    NotFoundError,
    TimeoutError,
)

DEFAULT_BASE_URL = "https://api2.freecustom.email/v1"
DEFAULT_TIMEOUT  = 10.0   # seconds
SDK_VERSION      = "1.0.0"


class HttpClient:
    """Async HTTP client. Used internally by all resource classes."""

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        retry_attempts: int = 2,
        retry_initial_delay: float = 0.5,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._retry_attempts = retry_attempts
        self._retry_initial_delay = retry_initial_delay

        self._headers = {
            "Authorization":  f"Bearer {api_key}",
            "Content-Type":   "application/json",
            "User-Agent":     f"freecustom-email-python/{SDK_VERSION}",
        }

    async def request(
        self,
        method: str,
        path: str,
        *,
        body: Optional[dict[str, Any]] = None,
    ) -> Any:
        """Make an authenticated request. Returns parsed JSON body."""
        url = f"{self._base_url}{path}"
        last_error: Exception = Exception("Request failed")

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            for attempt in range(self._retry_attempts + 1):
                if attempt > 0:
                    delay = self._retry_initial_delay * (2 ** (attempt - 1))
                    await asyncio.sleep(delay)

                try:
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=self._headers,
                        content=json.dumps(body).encode() if body is not None else None,
                    )
                    return self._handle_response(response)

                except httpx.TimeoutException:
                    last_error = TimeoutError(int(self._timeout * 1000))
                    continue  # retry on timeout

                except httpx.NetworkError as e:
                    last_error = FreecustomEmailError(f"Network error: {e}")
                    continue  # retry on network error

                except FreecustomEmailError:
                    raise  # don't retry API errors (4xx etc)

        raise last_error

    def _handle_response(self, response: httpx.Response) -> Any:
        try:
            body = response.json()
        except Exception:
            raise FreecustomEmailError(
                f"Failed to parse response (status {response.status_code})",
                status=response.status_code,
            )

        if response.is_success:
            return body

        message    = body.get("message") or response.reason_phrase
        error_code = body.get("error", "error")
        hint       = body.get("hint")
        upgrade_url = body.get("upgrade_url")

        status = response.status_code
        if status == 401:
            raise AuthError(message)
        if status == 403:
            raise PlanError(message, upgrade_url=upgrade_url)
        if status == 404:
            raise NotFoundError(message)
        if status == 429:
            retry_after_raw = response.headers.get("Retry-After", "1")
            try:
                retry_after = int(retry_after_raw)
            except ValueError:
                retry_after = 1
            raise RateLimitError(message, retry_after=retry_after)

        raise FreecustomEmailError(
            message,
            status=status,
            code=error_code,
            hint=hint,
            upgrade_url=upgrade_url,
        )


class SyncHttpClient:
    """
    Synchronous wrapper around HttpClient for use in non-async contexts.

    Usage::

        from freecustom_email import FreeCustomEmail

        client = FreeCustomEmail(api_key="fce_...", sync=True)
        inboxes = client.inboxes.list()   # no await needed
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        retry_attempts: int = 2,
        retry_initial_delay: float = 0.5,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._retry_attempts = retry_attempts
        self._retry_initial_delay = retry_initial_delay

        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type":  "application/json",
            "User-Agent":    f"freecustom-email-python/{SDK_VERSION}",
        }

    def request(
        self,
        method: str,
        path: str,
        *,
        body: Optional[dict[str, Any]] = None,
    ) -> Any:
        url = f"{self._base_url}{path}"
        last_error: Exception = Exception("Request failed")

        with httpx.Client(timeout=self._timeout) as client:
            for attempt in range(self._retry_attempts + 1):
                if attempt > 0:
                    import time
                    time.sleep(self._retry_initial_delay * (2 ** (attempt - 1)))

                try:
                    response = client.request(
                        method=method,
                        url=url,
                        headers=self._headers,
                        content=json.dumps(body).encode() if body is not None else None,
                    )
                    return self._handle_response(response)

                except httpx.TimeoutException:
                    last_error = TimeoutError(int(self._timeout * 1000))
                    continue
                except httpx.NetworkError as e:
                    last_error = FreecustomEmailError(f"Network error: {e}")
                    continue
                except FreecustomEmailError:
                    raise

        raise last_error

    def _handle_response(self, response: httpx.Response) -> Any:
        # Same logic as async version
        try:
            body = response.json()
        except Exception:
            raise FreecustomEmailError(
                f"Failed to parse response (status {response.status_code})",
                status=response.status_code,
            )
        if response.is_success:
            return body

        message    = body.get("message") or response.reason_phrase
        error_code = body.get("error", "error")
        hint       = body.get("hint")
        upgrade_url = body.get("upgrade_url")
        status = response.status_code

        if status == 401: raise AuthError(message)
        if status == 403: raise PlanError(message, upgrade_url=upgrade_url)
        if status == 404: raise NotFoundError(message)
        if status == 429:
            retry_after = int(response.headers.get("Retry-After", "1"))
            raise RateLimitError(message, retry_after=retry_after)
        raise FreecustomEmailError(message, status=status, code=error_code, hint=hint, upgrade_url=upgrade_url)
