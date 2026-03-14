"""Account resource."""
from __future__ import annotations
from ..http import HttpClient, SyncHttpClient
from ..types import AccountInfo, UsageStats


class AccountResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def info(self) -> AccountInfo:
        data = await self._http.request("GET", "/me")
        return AccountInfo.from_dict(data.get("data", data))

    async def usage(self) -> UsageStats:
        data = await self._http.request("GET", "/usage")
        return UsageStats.from_dict(data.get("data", data))


class SyncAccountResource:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def info(self) -> AccountInfo:
        data = self._http.request("GET", "/me")
        return AccountInfo.from_dict(data.get("data", data))

    def usage(self) -> UsageStats:
        data = self._http.request("GET", "/usage")
        return UsageStats.from_dict(data.get("data", data))
