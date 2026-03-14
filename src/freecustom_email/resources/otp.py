"""OTP resource."""
from __future__ import annotations
import asyncio
import time
from urllib.parse import quote
from ..http import HttpClient, SyncHttpClient
from ..types import OtpResult
from ..errors import WaitTimeoutError


class OtpResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def get(self, inbox: str) -> OtpResult:
        """Get the latest OTP from an inbox. Requires Growth plan+."""
        data = await self._http.request("GET", f"/inboxes/{quote(inbox)}/otp")
        return OtpResult.from_dict(data)

    async def wait_for(self, inbox: str, *, timeout_ms: int = 30_000, poll_interval_ms: int = 2_000) -> str:
        """
        Poll until an OTP arrives or timeout elapses. Returns the OTP string.

        Example::

            otp = await client.otp.wait_for("mytest@ditube.info", timeout_ms=30_000)
            print(otp)  # '482910'
        """
        deadline = time.monotonic() + timeout_ms / 1000
        while time.monotonic() < deadline:
            result = await self.get(inbox)
            if result.otp:
                return result.otp
            remaining = (deadline - time.monotonic()) * 1000
            if remaining <= 0:
                break
            await asyncio.sleep(min(poll_interval_ms, remaining) / 1000)
        raise WaitTimeoutError(inbox, timeout_ms)


class SyncOtpResource:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def get(self, inbox: str) -> OtpResult:
        data = self._http.request("GET", f"/inboxes/{quote(inbox)}/otp")
        return OtpResult.from_dict(data)

    def wait_for(self, inbox: str, *, timeout_ms: int = 30_000, poll_interval_ms: int = 2_000) -> str:
        deadline = time.monotonic() + timeout_ms / 1000
        while time.monotonic() < deadline:
            result = self.get(inbox)
            if result.otp:
                return result.otp
            remaining = (deadline - time.monotonic()) * 1000
            if remaining <= 0:
                break
            time.sleep(min(poll_interval_ms, remaining) / 1000)
        raise WaitTimeoutError(inbox, timeout_ms)
