"""Webhooks resource."""
from __future__ import annotations
from urllib.parse import quote
from ..http import HttpClient, SyncHttpClient
from ..types import Webhook, RegisterWebhookResult


class WebhooksResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    async def register(self, inbox: str, url: str) -> RegisterWebhookResult:
        data = await self._http.request("POST", "/webhooks", body={"inbox": inbox, "url": url})
        return RegisterWebhookResult.from_dict(data)

    async def list(self) -> list[Webhook]:
        data = await self._http.request("GET", "/webhooks")
        return [Webhook.from_dict(w) for w in data.get("data", [])]

    async def unregister(self, webhook_id: str) -> dict:
        return await self._http.request("DELETE", f"/webhooks/{quote(webhook_id)}")


class SyncWebhooksResource:
    def __init__(self, http: SyncHttpClient) -> None:
        self._http = http

    def register(self, inbox: str, url: str) -> RegisterWebhookResult:
        data = self._http.request("POST", "/webhooks", body={"inbox": inbox, "url": url})
        return RegisterWebhookResult.from_dict(data)

    def list(self) -> list[Webhook]:
        data = self._http.request("GET", "/webhooks")
        return [Webhook.from_dict(w) for w in data.get("data", [])]

    def unregister(self, webhook_id: str) -> dict:
        return self._http.request("DELETE", f"/webhooks/{quote(webhook_id)}")
