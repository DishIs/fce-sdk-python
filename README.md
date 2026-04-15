# 🧪 FreeCustom.Email — Auth Flow Testing & OTP Debugging SDK

[![PyPI](https://img.shields.io/pypi/v/freecustom-email)](https://pypi.org/project/freecustom-email/)
[![License](https://img.shields.io/github/license/DishIs/fce-sdk-python)](https://github.com/DishIs/fce-sdk-python/blob/main/LICENSE)

**Test, debug, and automate signup, OTP, and email-based authentication flows — with real-time observability.**

FreeCustom.Email is an API-first platform for developers and QA teams to:
- ✅ Create inboxes programmatically
- ✅ Receive emails in real-time
- ✅ Extract OTPs and verification links automatically
- ✅ Debug full auth flows with timeline + latency insights

## ⚡ Why this exists

Testing auth flows is painful:
- ❌ Flaky email delivery
- ❌ Polling delays
- ❌ OTP parsing issues
- ❌ No visibility into failures

FreeCustom.Email solves this by giving you: **👉 real-time auth flow debugging**.

---

## 📦 Installation

```bash
pip install freecustom-email
```

---

## 🚀 Quick Start (Auth Flow Testing)

```python
import asyncio
from freecustom_email import FreeCustomEmail

async def main():
    client = FreeCustomEmail(api_key="fce_your_api_key_here")
    email = "test@ditube.info"

    # 1. Create inbox (pass `is_testing=True` for zero-latency testing mode)
    await client.inboxes.register(email, is_testing=True)

    # 2. Start test run (NEW - Groups events in your timeline)
    await client.inboxes.start_test(email, "signup-test-1")

    # 3. Trigger your app (e.g. using httpx or playwright)
    # await httpx.post("https://yourapp.com/api/send-otp", json={"email": email})

    # 4. Wait for OTP
    otp = await client.otp.wait_for(email)
    print(f"OTP: {otp}")

    # 5. Debug the full flow
    timeline = await client.inboxes.get_timeline(email, "signup-test-1")
    print(timeline)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🔥 Debug Your Auth Flow

### Timeline (see what actually happened)
```python
timeline = await client.inboxes.get_timeline(email)
print(timeline)
# [
#   { "type": "smtp_rcpt_received", "time": 820 },
#   { "type": "email_received", "time": 830 },
#   { "type": "otp_extracted", "time": 835 },
#   { "type": "websocket_sent", "time": 840 }
# ]
```

### Insights (why your test failed)
```python
insights = await client.inboxes.get_insights(email)
print(insights)
# [
#   { "type": "slow_delivery", "message": "Email took >3s" },
#   { "type": "multiple_detected", "message": "Multiple emails detected" }
# ]
```

### Test Runs (group your flows)
```python
await client.inboxes.start_test(email, "signup-test-1")
timeline = await client.inboxes.get_timeline(email, "signup-test-1")
```

---

## ⚡ Real-time Debugging (WebSocket)

```python
import asyncio
from freecustom_email import FreeCustomEmail

async def main():
    client = FreeCustomEmail(api_key="fce_...")
    ws = client.realtime(mailbox="test@ditube.info")

    @ws.on("email")
    async def on_email(email):
        print(f"Flow update! OTP: {email.otp}")

    await ws.connect()
    await ws.wait()

asyncio.run(main())
```

---

## 🧪 Full Playwright Example

```python
import pytest
from playwright.async_api import Page
from freecustom_email import FreeCustomEmail
import os

client = FreeCustomEmail(api_key=os.getenv("FCE_API_KEY"))

@pytest.mark.asyncio
async def test_signup_flow(page: Page):
    email = "test@ditube.info"

    await client.inboxes.register(email, is_testing=True)
    await client.inboxes.start_test(email, "e2e-signup")

    await page.goto("https://yourapp.com/signup")
    await page.fill("#email", email)
    await page.click("button[type='submit']")

    # Automatically waits for the email and extracts the code
    otp = await client.otp.wait_for(email)

    await page.fill("#otp", otp)
    await page.click("#verify")

    # Debugging: View exactly how long delivery took
    timeline = await client.inboxes.get_timeline(email, "e2e-signup")
    print("Delivery Timeline:", timeline)
```

---

## 🔁 Old vs New Mental Model

| Old (Temp Mail) | New (FreeCustom.Email) |
| :--- | :--- |
| receive emails | **test auth flows** |
| read inbox | **debug flows** |
| parse OTP manually | **auto extract + analyze** |
| polling | **real-time events** |

---

## 📊 Plans (Updated Meaning)

| Plan | What you get |
| :--- | :--- |
| **Free** | basic inbox |
| **Startup** | real-time emails |
| **Growth** | OTP + debugging |
| **Enterprise** | full observability |

---

## 🔥 Most Important Methods (for devs)

- `await client.inboxes.start_test(email, test_id)`
- `await client.otp.wait_for(email)`
- `await client.inboxes.get_timeline(email, test_id)`
- `await client.inboxes.get_insights(email)`

---

