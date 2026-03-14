"""
Types — FreeCustom.Email Python SDK
All response models as dataclasses for clean attribute access.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Optional

# ── Plan ──────────────────────────────────────────────────────────────────────

ApiPlan = Literal["free", "developer", "startup", "growth", "enterprise"]

# ── Inbox ─────────────────────────────────────────────────────────────────────

@dataclass
class InboxObject:
    inbox: str
    local: str
    domain: str

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "InboxObject":
        return cls(inbox=d["inbox"], local=d["local"], domain=d["domain"])


@dataclass
class RegisterInboxResult:
    success: bool
    message: str
    inbox: str

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "RegisterInboxResult":
        return cls(success=d["success"], message=d.get("message", ""), inbox=d.get("inbox", ""))


@dataclass
class UnregisterInboxResult:
    success: bool
    message: str

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "UnregisterInboxResult":
        return cls(success=d["success"], message=d.get("message", ""))

# ── Message ───────────────────────────────────────────────────────────────────

@dataclass
class Attachment:
    filename: str
    content_type: str
    size: int
    content: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Attachment":
        return cls(
            filename=d.get("filename", ""),
            content_type=d.get("contentType", ""),
            size=d.get("size", 0),
            content=d.get("content"),
        )


@dataclass
class Message:
    id: str
    from_: str       # 'from' is a Python keyword — use from_
    to: str
    subject: str
    date: str
    text: Optional[str] = None
    html: Optional[str] = None
    otp: Optional[str] = None
    verification_link: Optional[str] = None
    has_attachment: bool = False
    was_attachment_stripped: bool = False
    attachments: list[Attachment] = field(default_factory=list)
    upgrade_hint: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Message":
        return cls(
            id=d["id"],
            from_=d.get("from", ""),
            to=d.get("to", ""),
            subject=d.get("subject", ""),
            date=d.get("date", ""),
            text=d.get("text"),
            html=d.get("html"),
            otp=d.get("otp"),
            verification_link=d.get("verificationLink"),
            has_attachment=d.get("hasAttachment", False),
            was_attachment_stripped=d.get("wasAttachmentStripped", False),
            attachments=[Attachment.from_dict(a) for a in d.get("attachments", [])],
            upgrade_hint=d.get("_upgrade_hint"),
        )


@dataclass
class DeleteMessageResult:
    success: bool
    message: str

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "DeleteMessageResult":
        return cls(success=d["success"], message=d.get("message", ""))

# ── OTP ───────────────────────────────────────────────────────────────────────

@dataclass
class OtpResult:
    success: bool
    otp: Optional[str]
    email_id: Optional[str] = None
    from_: Optional[str] = None
    subject: Optional[str] = None
    timestamp: Optional[int] = None
    verification_link: Optional[str] = None
    message: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "OtpResult":
        return cls(
            success=d["success"],
            otp=d.get("otp"),
            email_id=d.get("email_id"),
            from_=d.get("from"),
            subject=d.get("subject"),
            timestamp=d.get("timestamp"),
            verification_link=d.get("verification_link"),
            message=d.get("message"),
        )

# ── Domains ───────────────────────────────────────────────────────────────────

@dataclass
class DomainInfo:
    domain: str
    tier: str
    tags: list[str]
    expiring_soon: bool = False
    expires_at: Optional[str] = None
    expires_in_days: Optional[int] = None
    expired: bool = False

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "DomainInfo":
        return cls(
            domain=d["domain"],
            tier=d.get("tier", "free"),
            tags=d.get("tags", []),
            expiring_soon=d.get("expiring_soon", False),
            expires_at=d.get("expires_at"),
            expires_in_days=d.get("expires_in_days"),
            expired=d.get("expired", False),
        )


@dataclass
class DnsRecord:
    type: str
    hostname: str
    value: str
    priority: Optional[str] = None
    ttl: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "DnsRecord":
        return cls(
            type=d.get("type", ""),
            hostname=d.get("hostname", ""),
            value=d.get("value", ""),
            priority=d.get("priority"),
            ttl=d.get("ttl"),
        )


@dataclass
class CustomDomain:
    domain: str
    verified: bool
    mx_record: str
    txt_record: str
    added_at: Optional[str]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "CustomDomain":
        return cls(
            domain=d["domain"],
            verified=d.get("verified", False),
            mx_record=d.get("mx_record", ""),
            txt_record=d.get("txt_record", ""),
            added_at=d.get("added_at"),
        )


@dataclass
class AddCustomDomainResult:
    domain: str
    verified: bool
    mx_record: str
    txt_record: str
    added_at: str
    dns_records: list[DnsRecord]
    next_step: str

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "AddCustomDomainResult":
        return cls(
            domain=d["domain"],
            verified=d.get("verified", False),
            mx_record=d.get("mx_record", ""),
            txt_record=d.get("txt_record", ""),
            added_at=d.get("added_at", ""),
            dns_records=[DnsRecord.from_dict(r) for r in d.get("dns_records", [])],
            next_step=d.get("next_step", ""),
        )


@dataclass
class VerifyCustomDomainResult:
    success: bool
    verified: bool
    message: str
    domain: Optional[CustomDomain] = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "VerifyCustomDomainResult":
        return cls(
            success=d["success"],
            verified=d.get("verified", False),
            message=d.get("message", ""),
            domain=CustomDomain.from_dict(d["data"]) if d.get("data") else None,
        )


@dataclass
class RemoveCustomDomainResult:
    success: bool
    message: str
    inboxes_removed: list[str]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "RemoveCustomDomainResult":
        return cls(
            success=d["success"],
            message=d.get("message", ""),
            inboxes_removed=d.get("inboxes_removed", []),
        )

# ── Account ───────────────────────────────────────────────────────────────────

@dataclass
class RateLimits:
    requests_per_second: int
    requests_per_month: int

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "RateLimits":
        return cls(
            requests_per_second=d.get("requestsPerSecond", 0),
            requests_per_month=d.get("requestsPerMonth", 0),
        )


@dataclass
class PlanFeatures:
    otp_extraction: bool
    attachments: bool
    max_attachment_size_mb: int
    custom_domains: bool
    websocket: bool
    max_ws_connections: int

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "PlanFeatures":
        return cls(
            otp_extraction=d.get("otpExtraction", False),
            attachments=d.get("attachments", False),
            max_attachment_size_mb=d.get("maxAttachmentSizeMb", 0),
            custom_domains=d.get("customDomains", False),
            websocket=d.get("websocket", False),
            max_ws_connections=d.get("maxWsConnections", 0),
        )


@dataclass
class AccountInfo:
    plan: str
    plan_label: str
    price: str
    credits: int
    rate_limits: RateLimits
    features: PlanFeatures
    app_inboxes: list[str]
    app_inbox_count: int
    api_inboxes: list[str]
    api_inbox_count: int

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "AccountInfo":
        return cls(
            plan=d.get("plan", "free"),
            plan_label=d.get("plan_label", ""),
            price=d.get("price", ""),
            credits=d.get("credits", 0),
            rate_limits=RateLimits.from_dict(d.get("rate_limits", {})),
            features=PlanFeatures.from_dict(d.get("features", {})),
            app_inboxes=d.get("app_inboxes", []),
            app_inbox_count=d.get("app_inbox_count", 0),
            api_inboxes=d.get("api_inboxes", []),
            api_inbox_count=d.get("api_inbox_count", 0),
        )


@dataclass
class UsageStats:
    plan: str
    requests_used: int
    requests_limit: int
    requests_remaining: int
    percent_used: str
    credits_remaining: int
    resets: str

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "UsageStats":
        return cls(
            plan=d.get("plan", "free"),
            requests_used=d.get("requests_used", 0),
            requests_limit=d.get("requests_limit", 0),
            requests_remaining=d.get("requests_remaining", 0),
            percent_used=d.get("percent_used", "0.0%"),
            credits_remaining=d.get("credits_remaining", 0),
            resets=d.get("resets", ""),
        )

# ── Webhooks ──────────────────────────────────────────────────────────────────

@dataclass
class Webhook:
    id: str
    inbox: str
    url: str
    created_at: str
    failure_count: int = 0

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Webhook":
        return cls(
            id=str(d.get("_id", d.get("id", ""))),
            inbox=d.get("inbox", ""),
            url=d.get("url", ""),
            created_at=d.get("createdAt", ""),
            failure_count=d.get("failureCount", 0),
        )


@dataclass
class RegisterWebhookResult:
    success: bool
    id: str
    inbox: str
    url: str

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "RegisterWebhookResult":
        return cls(
            success=d["success"],
            id=d.get("id", ""),
            inbox=d.get("inbox", ""),
            url=d.get("url", ""),
        )

# ── WebSocket Events ──────────────────────────────────────────────────────────

@dataclass
class WsConnectedEvent:
    plan: str
    subscribed_inboxes: list[str]
    connection_count: int
    max_connections: int
    otp_extraction: bool
    attachments: bool

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "WsConnectedEvent":
        features = d.get("features", {})
        return cls(
            plan=d.get("plan", ""),
            subscribed_inboxes=d.get("subscribed_inboxes", []),
            connection_count=d.get("connection_count", 1),
            max_connections=d.get("max_connections", 0),
            otp_extraction=features.get("otp_extraction", False),
            attachments=features.get("attachments", False),
        )


@dataclass
class WsEmailEvent:
    id: str
    from_: str
    to: str
    subject: str
    date: str
    text: Optional[str] = None
    html: Optional[str] = None
    otp: Optional[str] = None
    verification_link: Optional[str] = None
    has_attachment: bool = False
    upgrade_hint: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "WsEmailEvent":
        return cls(
            id=d.get("id", ""),
            from_=d.get("from", ""),
            to=d.get("to", ""),
            subject=d.get("subject", ""),
            date=d.get("date", ""),
            text=d.get("text"),
            html=d.get("html"),
            otp=d.get("otp"),
            verification_link=d.get("verificationLink"),
            has_attachment=d.get("hasAttachment", False),
            upgrade_hint=d.get("_upgrade_hint"),
        )


@dataclass
class WsErrorEvent:
    code: str
    message: str
    upgrade_url: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "WsErrorEvent":
        return cls(
            code=d.get("code", "error"),
            message=d.get("message", ""),
            upgrade_url=d.get("upgrade_url"),
        )
