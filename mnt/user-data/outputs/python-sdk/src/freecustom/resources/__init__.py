"""Resources package."""
from .inboxes import InboxesResource
from .messages import MessagesResource
from .otp import OtpResource
from .domains import DomainsResource
from .webhooks import WebhooksResource
from .account import AccountResource

__all__ = [
    "InboxesResource",
    "MessagesResource",
    "OtpResource",
    "DomainsResource",
    "WebhooksResource",
    "AccountResource",
]
