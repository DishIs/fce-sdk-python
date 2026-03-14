"""
Tests — FreeCustom.Email Python SDK
Run: pytest
Requires: pip install pytest pytest-asyncio
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from freecustom import FreecustomEmailClient
from freecustom.errors import AuthError, PlanError, NotFoundError


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    return FreecustomEmailClient(api_key="fce_test_key")


@pytest.fixture
def sync_client():
    return FreecustomEmailClient(api_key="fce_test_key", sync=True)


# ── Auth ──────────────────────────────────────────────────────────────────────

def test_raises_on_empty_api_key():
    with pytest.raises(ValueError, match="api_key is required"):
        FreecustomEmailClient(api_key="")


# ── Account ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_account_info(client):
    mock_response = {
        "success": True,
        "data": {
            "plan": "developer",
            "plan_label": "Developer",
            "price": "$7/mo",
            "credits": 0,
            "rate_limits": {"requestsPerSecond": 10, "requestsPerMonth": 100000},
            "features": {
                "otpExtraction": False, "attachments": False,
                "maxAttachmentSizeMb": 0, "customDomains": False,
                "websocket": False, "maxWsConnections": 0,
            },
            "app_inboxes": [], "app_inbox_count": 0,
            "api_inboxes": ["test@ditube.info"], "api_inbox_count": 1,
        }
    }
    with patch.object(client.account._http, "request", new_callable=AsyncMock, return_value=mock_response):
        info = await client.account.info()
        assert info.plan == "developer"
        assert info.credits == 0
        assert info.api_inbox_count == 1


# ── Inboxes ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_inbox(client):
    mock = {"success": True, "message": "Inbox registered.", "inbox": "test@ditube.info"}
    with patch.object(client.inboxes._http, "request", new_callable=AsyncMock, return_value=mock):
        result = await client.inboxes.register("test@ditube.info")
        assert result.success is True
        assert result.inbox == "test@ditube.info"


@pytest.mark.asyncio
async def test_list_inboxes(client):
    mock = {"success": True, "data": [{"inbox": "test@ditube.info", "local": "test", "domain": "ditube.info"}]}
    with patch.object(client.inboxes._http, "request", new_callable=AsyncMock, return_value=mock):
        inboxes = await client.inboxes.list()
        assert len(inboxes) == 1
        assert inboxes[0].inbox == "test@ditube.info"
        assert inboxes[0].domain == "ditube.info"


# ── OTP ───────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_otp(client):
    mock = {
        "success": True,
        "otp": "482910",
        "email_id": "abc123",
        "from": "no-reply@github.com",
        "subject": "Verify your email",
        "timestamp": 1710234567000,
        "verification_link": "https://github.com/verify?code=482910",
    }
    with patch.object(client.otp._http, "request", new_callable=AsyncMock, return_value=mock):
        result = await client.otp.get("test@ditube.info")
        assert result.otp == "482910"
        assert result.verification_link == "https://github.com/verify?code=482910"


@pytest.mark.asyncio
async def test_otp_wait_for_immediate(client):
    mock = {"success": True, "otp": "123456"}
    with patch.object(client.otp._http, "request", new_callable=AsyncMock, return_value=mock):
        otp = await client.otp.wait_for("test@ditube.info", timeout_ms=5_000)
        assert otp == "123456"


# ── Error handling ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_auth_error_raised(client):
    with patch.object(client.account._http, "request", new_callable=AsyncMock, side_effect=AuthError()):
        with pytest.raises(AuthError):
            await client.account.info()


@pytest.mark.asyncio
async def test_plan_error_raised(client):
    with patch.object(client.otp._http, "request", new_callable=AsyncMock,
                      side_effect=PlanError("OTP requires Growth plan", upgrade_url="https://freecustom.email/pricing")):
        with pytest.raises(PlanError) as exc_info:
            await client.otp.get("test@ditube.info")
        assert exc_info.value.upgrade_url == "https://freecustom.email/pricing"


# ── Sync client ───────────────────────────────────────────────────────────────

def test_sync_list_inboxes(sync_client):
    mock = {"success": True, "data": [{"inbox": "sync@ditube.info", "local": "sync", "domain": "ditube.info"}]}
    with patch.object(sync_client.inboxes._http, "request", return_value=mock):
        inboxes = sync_client.inboxes.list()
        assert inboxes[0].inbox == "sync@ditube.info"
