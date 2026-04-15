"""Inboxes resource."""
from __future__ import annotations
from urllib.parse import quote
from typing import Union, Any
from ..http import HttpClient, SyncHttpClient
from ..types import InboxObject, RegisterInboxResult, UnregisterInboxResult


class InboxesResource:
    def __init__(self, http: Union[HttpClient, SyncHttpClient]) -> None:
        self._http = http
        self._is_async = isinstance(http, HttpClient)

    async def register(self, inbox: str, is_testing: bool | None = None) -> RegisterInboxResult:
        """Register a disposable inbox."""
        body: dict[str, Any] = {"inbox": inbox}
        if is_testing is not None:
            body["isTesting"] = is_testing
        data = await self._http.request("POST", "/inboxes", body=body)
        return RegisterInboxResult.from_dict(data)

    async def list_inboxes(self) -> list[InboxObject]:
        """List all registered inboxes."""
        data = await self._http.request("GET", "/inboxes")
        return [InboxObject.from_dict(d) for d in data.get("data", [])]

    # Keeping `list` for backwards compatibility
    list = list_inboxes

    async def unregister(self, inbox: str) -> UnregisterInboxResult:
        """Unregister an inbox."""
        data = await self._http.request("DELETE", f"/inboxes/{quote(inbox)}")
        return UnregisterInboxResult.from_dict(data)

    async def get_timeline(self, inbox: str) -> list[dict[str, Any]]:
        """Get the event timeline for a specific inbox."""
        data = await self._http.request("GET", f"/inboxes/{quote(inbox)}/timeline")
        return data.get("data", [])  # type: ignore

    async def get_insights(self, inbox: str) -> list[dict[str, Any]]:
        """Get delivery insights and failure flags for a specific inbox."""
        data = await self._http.request("GET", f"/inboxes/{quote(inbox)}/insights")
        return data.get("data", [])  # type: ignore


class SyncInboxesResource:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def register(self, inbox: str, is_testing: bool | None = None) -> RegisterInboxResult:
        body: dict[str, Any] = {"inbox": inbox}
        if is_testing is not None:
            body["isTesting"] = is_testing
        data = self._http.request("POST", "/inboxes", body=body)
        return RegisterInboxResult.from_dict(data)

    def list(self) -> list[InboxObject]:
        data = self._http.request("GET", "/inboxes")
        return [InboxObject.from_dict(d) for d in data.get("data", [])]

    def unregister(self, inbox: str) -> UnregisterInboxResult:
        data = self._http.request("DELETE", f"/inboxes/{quote(inbox)}")
        return UnregisterInboxResult.from_dict(data)

    def get_timeline(self, inbox: str) -> list[dict[str, Any]]:
        """Get the event timeline for a specific inbox."""
        data = self._http.request("GET", f"/inboxes/{quote(inbox)}/timeline")
        return data.get("data", [])  # type: ignore

    def get_insights(self, inbox: str) -> list[dict[str, Any]]:
        """Get delivery insights and failure flags for a specific inbox."""
        data = self._http.request("GET", f"/inboxes/{quote(inbox)}/insights")
        return data.get("data", [])  # type: ignore
