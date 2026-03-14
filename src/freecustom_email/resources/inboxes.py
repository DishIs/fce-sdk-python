"""Inboxes resource."""
from __future__ import annotations
from urllib.parse import quote
from typing import Union
from ..http import HttpClient, SyncHttpClient
from ..types import InboxObject, RegisterInboxResult, UnregisterInboxResult


class InboxesResource:
    def __init__(self, http: Union[HttpClient, SyncHttpClient]) -> None:
        self._http = http
        self._is_async = isinstance(http, HttpClient)

    async def register(self, inbox: str) -> RegisterInboxResult:
        """Register a disposable inbox."""
        data = await self._http.request("POST", "/inboxes", body={"inbox": inbox})
        return RegisterInboxResult.from_dict(data)

    async def list(self) -> list[InboxObject]:
        """List all registered inboxes."""
        data = await self._http.request("GET", "/inboxes")
        return [InboxObject.from_dict(d) for d in data.get("data", [])]

    async def unregister(self, inbox: str) -> UnregisterInboxResult:
        """Unregister an inbox."""
        data = await self._http.request("DELETE", f"/inboxes/{quote(inbox)}")
        return UnregisterInboxResult.from_dict(data)


class SyncInboxesResource:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def register(self, inbox: str) -> RegisterInboxResult:
        data = self._http.request("POST", "/inboxes", body={"inbox": inbox})
        return RegisterInboxResult.from_dict(data)

    def list(self) -> list[InboxObject]:
        data = self._http.request("GET", "/inboxes")
        return [InboxObject.from_dict(d) for d in data.get("data", [])]

    def unregister(self, inbox: str) -> UnregisterInboxResult:
        data = self._http.request("DELETE", f"/inboxes/{quote(inbox)}")
        return UnregisterInboxResult.from_dict(data)
