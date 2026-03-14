"""
FreeCustomEmail — FreeCustom.Email Python SDK main entry point.
Supports both async (default) and sync modes.
"""
from __future__ import annotations

from typing import Callable, Awaitable, Optional

from .http import HttpClient, SyncHttpClient, DEFAULT_BASE_URL, DEFAULT_TIMEOUT
from .ws_client import WsClient
from .resources.inboxes import InboxesResource, SyncInboxesResource
from .resources.messages import MessagesResource, SyncMessagesResource
from .resources.otp import OtpResource, SyncOtpResource
from .resources.domains import DomainsResource, SyncDomainsResource
from .resources.webhooks import WebhooksResource, SyncWebhooksResource
from .resources.account import AccountResource, SyncAccountResource


class FreeCustomEmail:
    """
    Async client for FreeCustom.Email API.

    Usage (async — recommended)::

        import asyncio
        from freecustom_email import FreeCustomEmail

        async def main():
            client = FreeCustomEmail(api_key="fce_...")

            await client.inboxes.register("mytest@ditube.info")
            otp = await client.otp.wait_for("mytest@ditube.info")
            print(otp)

        asyncio.run(main())

    Usage (sync)::

        client = FreeCustomEmail(api_key="fce_...", sync=True)
        client.inboxes.register("mytest@ditube.info")
        otp = client.otp.wait_for("mytest@ditube.info")
        print(otp)
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        retry_attempts: int = 2,
        retry_initial_delay: float = 0.5,
        sync: bool = False,
    ) -> None:
        if not api_key:
            raise ValueError("FreeCustom.Email SDK: api_key is required")

        self._api_key = api_key
        self._base_url = base_url
        self._sync = sync

        if sync:
            http = SyncHttpClient(
                api_key=api_key,
                base_url=base_url,
                timeout=timeout,
                retry_attempts=retry_attempts,
                retry_initial_delay=retry_initial_delay,
            )
            self.inboxes  = SyncInboxesResource(http)   # type: ignore[assignment]
            self.messages = SyncMessagesResource(http)   # type: ignore[assignment]
            self.otp      = SyncOtpResource(http)        # type: ignore[assignment]
            self.domains  = SyncDomainsResource(http)    # type: ignore[assignment]
            self.webhooks = SyncWebhooksResource(http)   # type: ignore[assignment]
            self.account  = SyncAccountResource(http)    # type: ignore[assignment]
        else:
            http_async = HttpClient(
                api_key=api_key,
                base_url=base_url,
                timeout=timeout,
                retry_attempts=retry_attempts,
                retry_initial_delay=retry_initial_delay,
            )
            self.inboxes  = InboxesResource(http_async)
            self.messages = MessagesResource(http_async)
            self.otp      = OtpResource(http_async)
            self.domains  = DomainsResource(http_async)
            self.webhooks = WebhooksResource(http_async)
            self.account  = AccountResource(http_async)

    def realtime(
        self,
        *,
        mailbox: Optional[str] = None,
        auto_reconnect: bool = True,
        reconnect_delay: float = 3.0,
        max_reconnect_attempts: int = 10,
        ping_interval: float = 30.0,
    ) -> WsClient:
        """
        Create a real-time WebSocket client. Requires Startup plan or above.

        Example::

            ws = client.realtime(mailbox="mytest@ditube.info")

            @ws.on("email")
            async def handle(email):
                print(email.otp)

            await ws.connect()
            await ws.wait()   # block until disconnected
        """
        # Convert HTTP URL to WebSocket URL
        ws_url = (
            self._base_url
            .replace("https://", "wss://")
            .replace("http://", "ws://")
        )
        return WsClient(
            api_key=self._api_key,
            base_ws_url=ws_url,
            mailbox=mailbox,
            auto_reconnect=auto_reconnect,
            reconnect_delay=reconnect_delay,
            max_reconnect_attempts=max_reconnect_attempts,
            ping_interval=ping_interval,
        )

    async def get_otp_for_inbox(
        self,
        inbox: str,
        trigger_fn: Callable[[], Awaitable[None]],
        *,
        timeout_ms: int = 30_000,
        auto_unregister: bool = True,
    ) -> str:
        """
        Convenience: register → trigger email → wait for OTP → unregister.
        Handles the full verification lifecycle in one call.

        Example::

            async def send_email():
                await httpx.AsyncClient().post(
                    "https://yourapp.com/api/signup",
                    json={"email": "mytest@ditube.info"},
                )

            otp = await client.get_otp_for_inbox(
                "mytest@ditube.info",
                send_email,
                timeout_ms=30_000,
            )
            print("OTP:", otp)
        """
        await self.inboxes.register(inbox)
        try:
            await trigger_fn()
            return await self.otp.wait_for(inbox, timeout_ms=timeout_ms)  # type: ignore[union-attr]
        finally:
            if auto_unregister:
                try:
                    await self.inboxes.unregister(inbox)  # type: ignore[union-attr]
                except Exception:
                    pass
