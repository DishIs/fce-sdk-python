# freecustom-email Python SDK

[![PyPI](https://img.shields.io/pypi/v/freecustom-email)](https://pypi.org/project/freecustom-email/)
[![License](https://img.shields.io/github/license/DishIs/fce-sdk-python)](https://github.com/DishIs/fce-sdk-python/blob/main/LICENSE)

Official Python SDK for [FreeCustom.Email](https://freecustom.email) — the ultimate API for disposable inboxes, automated OTP extraction, and real-time email delivery via WebSockets.

## 🚀 Features

- **Disposable Inboxes**: Instantly register and manage temporary email addresses.
- **Automated OTP Extraction**: Automatically extract verification codes from incoming emails.
- **Real-time Delivery**: Receive emails instantly via high-performance WebSockets.
- **Async & Sync Support**: Native `asyncio` support with an optional synchronous interface.
- **Custom Domains**: Manage and verify your own custom domains for personalized temporary mail.
- **Webhooks**: Programmatically manage HTTP webhooks for email notifications.
- **Type-Safe**: Full typing support for a better developer experience.

---

## 📦 Installation

```bash
pip install freecustom-email
```

---

## 🛠 Quick Start

### 1. Initialize the Client

Get your API key from the [FreeCustom.Email Dashboard](https://freecustom.email/api/dashboard).

```python
from freecustom_email import FreeCustomEmail

client = FreeCustomEmail(api_key="fce_your_api_key")
```

### 2. Async Usage (Recommended)

```python
import asyncio
from freecustom_email import FreeCustomEmail

async def main():
    client = FreeCustomEmail(api_key="fce_...")

    # Register an inbox (pass is_testing=True for zero-latency testing, Growth plan+)
    await client.inboxes.register("test@ditube.info", is_testing=True)
    print("Inbox registered!")

    # Wait for an OTP (Growth plan+)
    print("Waiting for OTP...")
    otp = await client.otp.wait_for("test@ditube.info", timeout_ms=60_000)
    print(f"Your OTP is: {otp}")

    # List recent messages
    messages = await client.messages.list("test@ditube.info")
    for msg in messages:
        print(f"Subject: {msg.subject} | From: {msg.from_}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Sync Usage

```python
from freecustom_email import FreeCustomEmail

client = FreeCustomEmail(api_key="fce_...", sync=True)

# Register and wait (pass is_testing=True for zero-latency testing)
client.inboxes.register("sync-test@ditube.info", is_testing=True)
otp = client.otp.wait_for("sync-test@ditube.info")
print(f"OTP received: {otp}")
```

---

## ⚡️ Real-time WebSockets

Connect to our WebSocket server to receive emails instantly as they arrive.

```python
import asyncio
from freecustom_email import FreeCustomEmail

async def main():
    client = FreeCustomEmail(api_key="fce_...")
    
    # Subscribe to a specific mailbox or all emails on your plan
    ws = client.realtime(mailbox="test@ditube.info")

    @ws.on("connected")
    async def on_connect(info):
        print(f"Connected! Subscribed inboxes: {info.subscribed_inboxes}")

    @ws.on("email")
    async def on_email(email):
        print(f"New Email! Subject: {email.subject}")
        if email.otp:
            print(f"Extracted OTP: {email.otp}")

    @ws.on("error")
    async def on_error(event):
        print(f"WS Error: {event.message}")

    await ws.connect()
    await ws.wait() # Block and keep listening

asyncio.run(main())
```

---

## 🧩 Advanced Features

### Automated Verification Flow
The `get_otp_for_inbox` helper handles the entire lifecycle: **register → trigger → wait → unregister**.

```python
async def trigger_signup():
    # Your code to click "Send OTP" on a website
    pass

otp = await client.get_otp_for_inbox(
    inbox="verify@ditube.info",
    trigger_fn=trigger_signup,
    timeout_ms=30_000
)
```

### Custom Domains
Manage your own domains directly through the SDK.

```python
# Add a new custom domain
result = await client.domains.add("my-temp-mail.com")

# Check verification status
status = await client.domains.verify("my-temp-mail.com")
if status.verified:
    print("Domain is ready to use!")
```

---

## 🛡 Error Handling

The SDK provides typed exceptions for precise error management.

```python
from freecustom.errors import AuthError, PlanError, RateLimitError, WaitTimeoutError

try:
    await client.inboxes.register("test@invalid")
except AuthError:
    print("Invalid API key.")
except PlanError as e:
    print(f"Plan limit reached. Upgrade at: {e.upgrade_url}")
except WaitTimeoutError:
    print("No email arrived within the timeout period.")
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- [Official Website](https://freecustom.email)
- [API Documentation](https://freecustom.email/api/docs)
- [Dashboard](https://freecustom.email/api/dashboard)
- [Support](mailto:support@freecustom.email)

### Observability & Debugging

```python
# Fetch the event timeline for an inbox
timeline = client.inboxes.get_timeline('test@domain.com')
print(timeline)

# Fetch failure insights and warnings
insights = client.inboxes.get_insights('test@domain.com')
print(insights)
```
