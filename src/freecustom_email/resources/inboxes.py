"""Inboxes resource."""
from __future__ import annotations
from urllib.parse import quote
from typing import Union, Any
from ..http import HttpClient, SyncHttpClient
from ..types import InboxObject, RegisterInboxResult, UnregisterInboxResult, StartTestResult


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

    async def start_test(self, inbox: str, test_id: str | None = None) -> StartTestResult:
        """Start a new test boundary for this inbox."""
        body: dict[str, Any] = {}
        if test_id is not None:
            body["test_id"] = test_id
        data = await self._http.request("POST", f"/inboxes/{quote(inbox)}/tests", body=body)
        return StartTestResult.from_dict(data)

    async def get_timeline(self, inbox: str, test_id: str | None = None) -> list[dict[str, Any]]:
        """Get the event timeline for a specific inbox."""
        query = f"?test_id={quote(test_id)}" if test_id else ""
        data = await self._http.request("GET", f"/inboxes/{quote(inbox)}/timeline{query}")
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

    def start_test(self, inbox: str, test_id: str | None = None) -> StartTestResult:
        """Start a new test boundary for this inbox."""
        body: dict[str, Any] = {}
        if test_id is not None:
            body["test_id"] = test_id
        data = self._http.request("POST", f"/inboxes/{quote(inbox)}/tests", body=body)
        return StartTestResult.from_dict(data)

    def get_timeline(self, inbox: str, test_id: str | None = None) -> list[dict[str, Any]]:
        """Get the event timeline for a specific inbox."""
        query = f"?test_id={quote(test_id)}" if test_id else ""
        data = self._http.request("GET", f"/inboxes/{quote(inbox)}/timeline{query}")
        return data.get("data", [])  # type: ignore

    def get_insights(self, inbox: str) -> list[dict[str, Any]]:
        """Get delivery insights and failure flags for a specific inbox."""
        data = self._http.request("GET", f"/inboxes/{quote(inbox)}/insights")
        return data.get("data", [])  # type: ignore
