# freecustom-email Python SDK — PyPI Publish Guide
# ─────────────────────────────────────────────────────────────────────────────

══════════════════════════════════════════════════════════════
FILE STRUCTURE
══════════════════════════════════════════════════════════════

freecustom-email/
├── pyproject.toml            ← packaging config (replaces setup.py)
├── README.md
├── LICENSE
├── src/
│   └── freecustom-email/
│       ├── __init__.py       ← public exports
│       ├── client.py         ← FreecustomEmailClient (async + sync)
│       ├── http.py           ← httpx-based HTTP client
│       ├── ws_client.py      ← websockets-based WS client
│       ├── types.py          ← all dataclasses
│       ├── errors.py         ← typed exception hierarchy
│       └── resources/
│           ├── __init__.py
│           ├── inboxes.py
│           ├── messages.py
│           ├── otp.py
│           ├── domains.py
│           ├── webhooks.py
│           └── account.py
└── tests/
    └── test_client.py

══════════════════════════════════════════════════════════════
STEP 1 — ENVIRONMENT
══════════════════════════════════════════════════════════════

python --version   # must be >= 3.9

# Create virtual environment
python -m venv .venv
source .venv/bin/activate     # Linux/Mac
# .venv\Scripts\activate      # Windows

# Install the package in editable mode + dev deps
pip install -e ".[dev]"

# This installs: httpx, websockets, pytest, pytest-asyncio, mypy, ruff

══════════════════════════════════════════════════════════════
STEP 2 — RUN TESTS
══════════════════════════════════════════════════════════════

pytest

# Expected output:
#   tests/test_client.py ........
#   8 passed in 0.XXs

══════════════════════════════════════════════════════════════
STEP 3 — TYPE CHECK
══════════════════════════════════════════════════════════════

mypy src/

# Must pass with no errors before publishing

══════════════════════════════════════════════════════════════
STEP 4 — LINT
══════════════════════════════════════════════════════════════

ruff check src/
ruff format src/   # auto-format

══════════════════════════════════════════════════════════════
STEP 5 — BUILD THE DISTRIBUTION
══════════════════════════════════════════════════════════════

# Install build tools
pip install build twine

# Build both wheel and source distribution
python -m build

# Creates:
#   dist/freecustom_email-1.0.0-py3-none-any.whl   ← wheel (fast install)
#   dist/freecustom_email-1.0.0.tar.gz             ← source dist

# Inspect the wheel contents:
python -m zipfile -l dist/freecustom_email-1.0.0-py3-none-any.whl

══════════════════════════════════════════════════════════════
STEP 6 — TEST LOCALLY
══════════════════════════════════════════════════════════════

# Install from local wheel in a fresh environment
pip install dist/freecustom_email-1.0.0-py3-none-any.whl

python << 'EOF'
from freecustom import FreecustomEmailClient
import asyncio

async def test():
    client = FreecustomEmailClient(api_key="fce_your_real_key")
    info = await client.account.info()
    print("Plan:", info.plan)
    print("Credits:", info.credits)

asyncio.run(test())
EOF

══════════════════════════════════════════════════════════════
STEP 7 — CREATE PyPI ACCOUNT + API TOKEN
══════════════════════════════════════════════════════════════

1. Go to https://pypi.org/account/register/
2. Verify your email
3. Go to https://pypi.org/manage/account/token/
4. Create a token — name: "freecustom-email publish"
   Scope: Entire account (for first publish) or project-scoped after
5. Copy the token — starts with pypi-

# Configure credentials (~/.pypirc):
cat > ~/.pypirc << 'CONF'
[pypi]
  username = __token__
  password = pypi-your-token-here
CONF
chmod 600 ~/.pypirc

══════════════════════════════════════════════════════════════
STEP 8 — TEST ON TestPyPI FIRST (recommended)
══════════════════════════════════════════════════════════════

# Register on test.pypi.org separately
# Create a TestPyPI token at https://test.pypi.org/manage/account/token/

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Install from TestPyPI to verify
pip install --index-url https://test.pypi.org/simple/ freecustom-email

# Test it works, then proceed to real PyPI

══════════════════════════════════════════════════════════════
STEP 9 — PUBLISH TO PyPI
══════════════════════════════════════════════════════════════

# Check distribution files are valid
twine check dist/*

# Upload
twine upload dist/*

# Output:
#   Uploading freecustom_email-1.0.0-py3-none-any.whl
#   Uploading freecustom_email-1.0.0.tar.gz
#   View at: https://pypi.org/project/freecustom-email/1.0.0/

# Verify install works
pip install freecustom-email
python -c "import freecustom; print(freecustom.__version__)"

══════════════════════════════════════════════════════════════
STEP 10 — PUBLISHING UPDATES
══════════════════════════════════════════════════════════════

1. Update version in pyproject.toml (e.g. "1.0.0" → "1.0.1")
2. Rebuild: python -m build
3. Re-upload: twine upload dist/*

NOTE: PyPI does not allow re-uploading the same version.
You MUST bump the version for every publish.

══════════════════════════════════════════════════════════════
USAGE EXAMPLES
══════════════════════════════════════════════════════════════

── INSTALL ──────────────────────────────────────────────────

    pip install freecustom-email

── ASYNC (recommended) ──────────────────────────────────────

    import asyncio
    from freecustom import FreecustomEmailClient

    async def main():
        client = FreecustomEmailClient(api_key="fce_...")

        # Register inbox
        await client.inboxes.register("mytest@ditube.info")

        # Get messages
        messages = await client.messages.list("mytest@ditube.info")
        for msg in messages:
            print(msg.subject, msg.otp)

        # Wait for OTP (Growth plan+)
        otp = await client.otp.wait_for("mytest@ditube.info", timeout_ms=30_000)
        print("OTP:", otp)

        # Full flow helper
        otp = await client.get_otp_for_inbox(
            "mytest@ditube.info",
            trigger_fn=lambda: httpx.AsyncClient().post("https://yourapp.com/signup"),
        )

        # Account info
        info = await client.account.info()
        print(f"Plan: {info.plan}, Credits: {info.credits}")

        # Unregister
        await client.inboxes.unregister("mytest@ditube.info")

    asyncio.run(main())

── SYNC ─────────────────────────────────────────────────────

    from freecustom import FreecustomEmailClient

    client = FreecustomEmailClient(api_key="fce_...", sync=True)

    client.inboxes.register("mytest@ditube.info")
    messages = client.messages.list("mytest@ditube.info")
    otp = client.otp.wait_for("mytest@ditube.info")
    print("OTP:", otp)

── WEBSOCKET ─────────────────────────────────────────────────

    import asyncio
    from freecustom import FreecustomEmailClient

    async def main():
        client = FreecustomEmailClient(api_key="fce_...")

        ws = client.realtime(mailbox="mytest@ditube.info")

        @ws.on("connected")
        async def on_connect(info):
            print(f"Connected — plan: {info.plan}")
            print(f"Subscribed: {info.subscribed_inboxes}")

        @ws.on("email")
        async def on_email(email):
            print(f"New email from {email.from_}")
            print(f"Subject: {email.subject}")
            print(f"OTP: {email.otp}")

        @ws.on("disconnected")
        async def on_disconnect(code, reason):
            print(f"Disconnected: {code} {reason}")

        @ws.on("reconnecting")
        async def on_reconnect(attempt, max_attempts):
            print(f"Reconnecting {attempt}/{max_attempts}...")

        await ws.connect()
        await ws.wait()    # block until disconnected

    asyncio.run(main())

── ERROR HANDLING ────────────────────────────────────────────

    from freecustom import FreecustomEmailClient
    from freecustom.errors import (
        AuthError, PlanError, RateLimitError,
        NotFoundError, TimeoutError, WaitTimeoutError,
    )

    try:
        otp = await client.otp.wait_for("mytest@ditube.info")
    except AuthError:
        print("Invalid API key")
    except PlanError as e:
        print(f"Plan too low: {e}")
        print(f"Upgrade at: {e.upgrade_url}")
    except RateLimitError as e:
        print(f"Rate limited. Retry after {e.retry_after}s")
    except WaitTimeoutError as e:
        print(f"No OTP arrived in {e.timeout_ms}ms")
    except NotFoundError:
        print("Inbox not found")

══════════════════════════════════════════════════════════════
POST-PUBLISH CHECKLIST
══════════════════════════════════════════════════════════════

□ Package visible at: https://pypi.org/project/freecustom-email/
□ pip install freecustom-email works
□ README renders correctly on PyPI page
□ mypy src/ passes with no errors
□ Add badge to your docs:
    [![PyPI](https://img.shields.io/pypi/v/freecustom-email)](https://pypi.org/project/freecustom-email/)
□ Add to freecustom.email/docs/api:
    pip install freecustom-email
