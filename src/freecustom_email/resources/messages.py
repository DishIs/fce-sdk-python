"""Messages resource."""
from __future__ import annotations
import asyncio
from urllib.parse import quote
from typing import Callable, Optional, Union
from ..http import HttpClient, SyncHttpClient
from ..types import Message, DeleteMessageResult
from ..errors import WaitTimeoutError


class MessagesResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def list(self, inbox: str) -> list[Message]:
        data = await self._http.request("GET", f"/inboxes/{quote(inbox)}/messages")
        return [Message.from_dict(m) for m in data.get("data", [])]

    async def get(self, inbox: str, message_id: str) -> Message:
        data = await self._http.request("GET", f"/inboxes/{quote(inbox)}/messages/{quote(message_id)}")
        return Message.from_dict(data.get("data", data))

    async def delete(self, inbox: str, message_id: str) -> DeleteMessageResult:
        data = await self._http.request("DELETE", f"/inboxes/{quote(inbox)}/messages/{quote(message_id)}")
        return DeleteMessageResult.from_dict(data)

    async def wait_for(
        self,
        inbox: str,
        *,
        timeout_ms: int = 30_000,
        poll_interval_ms: int = 2_000,
        match: Optional[Callable[[Message], bool]] = None,
    ) -> Message:
        """
        Poll until a matching message arrives or timeout elapses.

        Example::

            msg = await client.messages.wait_for(
                "mytest@ditube.info",
                timeout_ms=30_000,
                match=lambda m: "github" in m.from_,
            )
        """
        import time
        deadline = time.monotonic() + timeout_ms / 1000

        while time.monotonic() < deadline:
            messages = await self.list(inbox)
            found = next((m for m in messages if match(m)), None) if match else (messages[0] if messages else None)
            if found:
                return found
            remaining = (deadline - time.monotonic()) * 1000
            if remaining <= 0:
                break
            await asyncio.sleep(min(poll_interval_ms, remaining) / 1000)

        raise WaitTimeoutError(inbox, timeout_ms)


class SyncMessagesResource:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def list(self, inbox: str) -> list[Message]:
        data = self._http.request("GET", f"/inboxes/{quote(inbox)}/messages")
        return [Message.from_dict(m) for m in data.get("data", [])]

    def get(self, inbox: str, message_id: str) -> Message:
        data = self._http.request("GET", f"/inboxes/{quote(inbox)}/messages/{quote(message_id)}")
        return Message.from_dict(data.get("data", data))

    def delete(self, inbox: str, message_id: str) -> DeleteMessageResult:
        data = self._http.request("DELETE", f"/inboxes/{quote(inbox)}/messages/{quote(message_id)}")
        return DeleteMessageResult.from_dict(data)

    def wait_for(self, inbox: str, *, timeout_ms: int = 30_000, poll_interval_ms: int = 2_000,
                 match: Optional[Callable[[Message], bool]] = None) -> Message:
        import time
        deadline = time.monotonic() + timeout_ms / 1000
        while time.monotonic() < deadline:
            messages = self.list(inbox)
            found = next((m for m in messages if match(m)), None) if match else (messages[0] if messages else None)
            if found:
                return found
            remaining = (deadline - time.monotonic()) * 1000
            if remaining <= 0:
                break
            time.sleep(min(poll_interval_ms, remaining) / 1000)
        raise WaitTimeoutError(inbox, timeout_ms)
