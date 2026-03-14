"""
FreeCustom.Email Python SDK
Official client for the FreeCustom.Email API.

Usage::

    from freecustom import FreecustomEmailClient

    client = FreecustomEmailClient(api_key="fce_your_key")

    # Register inbox
    await client.inboxes.register("mytest@ditube.info")

    # Get OTP
    otp = await client.otp.wait_for("mytest@ditube.info")
    print(otp)  # '482910'

    # Real-time WebSocket
    ws = client.realtime(mailbox="mytest@ditube.info")

    @ws.on("email")
    async def handle_email(email):
        print(email.subject, email.otp)

    await ws.connect()
"""

from .client import FreecustomEmailClient
from .ws_client import WsClient
from .errors import (
    FreecustomEmailError,
    AuthError,
    PlanError,
    RateLimitError,
    NotFoundError,
    TimeoutError,
)
from .types import (
    ApiPlan,
    InboxObject,
    RegisterInboxResult,
    Message,
    Attachment,
    OtpResult,
    DomainInfo,
    CustomDomain,
    AddCustomDomainResult,
    VerifyCustomDomainResult,
    RemoveCustomDomainResult,
    AccountInfo,
    UsageStats,
    Webhook,
    WsConnectedEvent,
    WsEmailEvent,
    WsErrorEvent,
)

__version__ = "1.0.0"
__all__ = [
    "FreecustomEmailClient",
    "WsClient",
    # Errors
    "FreecustomEmailError",
    "AuthError",
    "PlanError",
    "RateLimitError",
    "NotFoundError",
    "TimeoutError",
    # Types
    "ApiPlan",
    "InboxObject",
    "RegisterInboxResult",
    "Message",
    "Attachment",
    "OtpResult",
    "DomainInfo",
    "CustomDomain",
    "AddCustomDomainResult",
    "VerifyCustomDomainResult",
    "RemoveCustomDomainResult",
    "AccountInfo",
    "UsageStats",
    "Webhook",
    "WsConnectedEvent",
    "WsEmailEvent",
    "WsErrorEvent",
]
