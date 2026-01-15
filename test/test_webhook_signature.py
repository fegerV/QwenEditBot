#!/usr/bin/env python3

"""Test YuKassa webhook signature verification.

This is a lightweight integration test (no pytest required):
- Missing signature -> 401
- Invalid signature -> 401
- Valid signature -> 200
"""

import asyncio
import hashlib
import hmac
import json
import os
import sys


def _make_signature(secret: str, body: str) -> str:
    return hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()


async def main() -> None:
    root_dir = os.path.dirname(__file__)
    sys.path.append(os.path.join(root_dir, "backend"))

    os.environ.setdefault("BOT_TOKEN", "test-bot-token")
    os.environ.setdefault("WEEKLY_BONUS_ENABLED", "false")

    secret = "test-secret"
    os.environ["YUKASSA_WEBHOOK_SECRET"] = secret

    from app.main import app  # noqa: E402

    payload = {
        "type": "notification",
        "event": "payment.succeeded",
        "object": {
            "id": "test-payment-id",
            "status": "succeeded",
            "amount": {"value": "100.00", "currency": "RUB"},
            "currency": "RUB",
            "created_at": "2024-01-01T00:00:00Z",
        },
    }

    body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    valid_signature = _make_signature(secret, body)

    import httpx  # noqa: E402

    transport = httpx.ASGITransport(app=app, lifespan="on")
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Missing signature
        r = await client.post(
            "/api/webhooks/yukassa",
            content=body.encode(),
            headers={"Content-Type": "application/json"},
        )
        assert r.status_code == 401, r.text

        # Invalid signature
        r = await client.post(
            "/api/webhooks/yukassa",
            content=body.encode(),
            headers={
                "Content-Type": "application/json",
                "X-Yookassa-Signature": "invalid",
            },
        )
        assert r.status_code == 401, r.text

        # Valid signature
        r = await client.post(
            "/api/webhooks/yukassa",
            content=body.encode(),
            headers={
                "Content-Type": "application/json",
                "X-Yookassa-Signature": valid_signature,
            },
        )
        assert r.status_code == 200, r.text
        assert r.json().get("status") in {"ok", "ignored"}, r.text

    print("✅ YuKassa webhook signature verification works")


if __name__ == "__main__":
    asyncio.run(main())
