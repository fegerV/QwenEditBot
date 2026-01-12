import hashlib
import hmac
from typing import Optional


def verify_hmac_sha256_signature(
    body: bytes,
    signature: Optional[str],
    secret: str,
) -> bool:
    if not signature:
        return False

    expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)
