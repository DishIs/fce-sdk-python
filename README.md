# FreeCustom.Email Python SDK

Official Python SDK for [FreeCustom.Email](https://freecustom.email) — disposable inboxes, OTP extraction, and real-time WebSocket delivery.

## Installation

```bash
pip install freecustom-email
```

## Quick Start

```python
import asyncio
from freecustom import FreecustomEmailClient

async def main():
    client = FreecustomEmailClient(api_key="fce_...")
    
    # Register an inbox
    await client.inboxes.register("test@example.com")
    
    # Wait for OTP
    otp = await client.otp.wait_for("test@example.com")
    print(f"Your OTP is: {otp}")

if __name__ == "__main__":
    asyncio.run(main())
```
