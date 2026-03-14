"""
WebSocket client — FreeCustom.Email Python SDK
Built on websockets library. Handles auto-reconnect, ping/pong, typed events.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Awaitable, Callable, Optional
from urllib.parse import urlencode

from .types import WsConnectedEvent, WsEmailEvent, WsErrorEvent

logger = logging.getLogger("freecustom.ws")

# Handler types
EmailHandler    = Callable[[WsEmailEvent],    Awaitable[None]]
ConnectedHandler = Callable[[WsConnectedEvent], Awaitable[None]]
ErrorHandler    = Callable[[WsErrorEvent],    Awaitable[None]]
DisconnectHandler = Callable[[int, str],       Awaitable[None]]
ReconnectHandler  = Callable[[int, int],       Awaitable[None]]


class WsClient:
    """
    Real-time WebSocket client for FreeCustom.Email.
    Requires Startup plan or above.

    Usage::

        ws = client.realtime(mailbox="mytest@ditube.info")

        @ws.on("email")
        async def handle(email):
            print(email.subject, email.otp)

        @ws.on("connected")
        async def on_connect(info):
            print("Connected — plan:", info.plan)

        await ws.connect()
        # ws runs in background — await ws.wait() to block until disconnected
        await ws.wait()

        # Or disconnect manually:
        await ws.disconnect()
    """

    def __init__(
        self,
        api_key: str,
        base_ws_url: str,
        *,
        mailbox: Optional[str] = None,
        auto_reconnect: bool = True,
        reconnect_delay: float = 3.0,
        max_reconnect_attempts: int = 10,
        ping_interval: float = 30.0,
    ) -> None:
        self._api_key = api_key
        self._base_ws_url = base_ws_url.rstrip("/")
        self._mailbox = mailbox
        self._auto_reconnect = auto_reconnect
        self._reconnect_delay = reconnect_delay
        self._max_reconnect_attempts = max_reconnect_attempts
        self._ping_interval = ping_interval

        self._ws: Any = None  # websockets.WebSocketClientProtocol
        self._reconnect_attempts = 0
        self._closed = False
        self._done_event = asyncio.Event()

        # Event handlers: event_name → list of async callables
        self._handlers: dict[str, list[Callable[..., Awaitable[None]]]] = {
            "connected":    [],
            "email":        [],
            "error":        [],
            "disconnected": [],
            "reconnecting": [],
        }

    # ── Decorator-style event registration ────────────────────────────────────

    def on(self, event: str) -> Callable:
        """
        Register an async event handler using decorator syntax.

        @ws.on("email")
        async def handle_email(email: WsEmailEvent):
            print(email.otp)
        """
        def decorator(fn: Callable[..., Awaitable[None]]) -> Callable:
            self._handlers.setdefault(event, []).append(fn)
            return fn
        return decorator

    def add_listener(self, event: str, handler: Callable[..., Awaitable[None]]) -> None:
        """Register a handler imperatively."""
        self._handlers.setdefault(event, []).append(handler)

    def remove_listener(self, event: str, handler: Callable[..., Awaitable[None]]) -> None:
        """Remove a previously registered handler."""
        if event in self._handlers:
            self._handlers[event] = [h for h in self._handlers[event] if h is not handler]

    # ── Connection ─────────────────────────────────────────────────────────────

    async def connect(self) -> None:
        """Connect to the WebSocket and start the receive loop in the background."""
        self._closed = False
        self._done_event.clear()
        asyncio.create_task(self._run())

    async def disconnect(self) -> None:
        """Close the WebSocket connection cleanly."""
        self._closed = True
        if self._ws is not None:
            await self._ws.close()
        self._done_event.set()

    async def wait(self) -> None:
        """Block until the connection is closed (useful in scripts)."""
        await self._done_event.wait()

    @property
    def is_connected(self) -> bool:
        return self._ws is not None and not self._ws.closed

    # ── Internal ───────────────────────────────────────────────────────────────

    def _build_url(self) -> str:
        base = self._base_ws_url
        # Convert https → wss, http → ws if needed
        if base.startswith("https"):
            base = "wss" + base[5:]
        elif base.startswith("http"):
            base = "ws" + base[4:]

        params: dict[str, str] = {"api_key": self._api_key}
        if self._mailbox:
            params["mailbox"] = self._mailbox

        return f"{base}/ws?{urlencode(params)}"

    async def _run(self) -> None:
        """Main connection loop with auto-reconnect."""
        try:
            import websockets
        except ImportError:
            raise ImportError(
                "websockets is required for WebSocket support. "
                "Install it: pip install 'freecustom-email[ws]'"
            )

        url = self._build_url()

        while not self._closed:
            try:
                async with websockets.connect(
                    url,
                    ping_interval=None,  # we handle pings manually
                    close_timeout=5,
                ) as ws:
                    self._ws = ws
                    self._reconnect_attempts = 0
                    await self._receive_loop(ws)

            except Exception as e:
                if self._closed:
                    break

                logger.debug("WebSocket disconnected: %s", e)

                if not self._auto_reconnect:
                    break

                if self._reconnect_attempts >= self._max_reconnect_attempts:
                    logger.warning("Max reconnect attempts reached")
                    break

                self._reconnect_attempts += 1
                delay = self._reconnect_delay * (1.5 ** (self._reconnect_attempts - 1))

                await self._emit("reconnecting", self._reconnect_attempts, self._max_reconnect_attempts)
                await asyncio.sleep(delay)

        self._done_event.set()

    async def _receive_loop(self, ws: Any) -> None:
        """Handle incoming messages and send pings."""
        ping_task = asyncio.create_task(self._ping_loop(ws))

        try:
            async for raw in ws:
                try:
                    data: dict[str, Any] = json.loads(raw)
                except json.JSONDecodeError:
                    continue

                event_type = data.get("type", "")

                if event_type == "connected":
                    await self._emit("connected", WsConnectedEvent.from_dict(data))

                elif event_type == "pong":
                    pass  # keepalive acknowledged

                elif event_type == "error":
                    await self._emit("error", WsErrorEvent.from_dict(data))

                else:
                    # All other frames are email events
                    await self._emit("email", WsEmailEvent.from_dict(data))

        finally:
            ping_task.cancel()
            code   = ws.close_code or 1006
            reason = ws.close_reason or ""
            await self._emit("disconnected", code, reason)

    async def _ping_loop(self, ws: Any) -> None:
        """Send ping frames on an interval to keep the connection alive."""
        while True:
            await asyncio.sleep(self._ping_interval)
            try:
                await ws.send(json.dumps({"type": "ping"}))
            except Exception:
                break

    async def _emit(self, event: str, *args: Any) -> None:
        """Call all handlers for an event, catching exceptions so one bad handler doesn't kill others."""
        for handler in self._handlers.get(event, []):
            try:
                await handler(*args)
            except Exception as e:
                logger.exception("Error in %s handler: %s", event, e)
