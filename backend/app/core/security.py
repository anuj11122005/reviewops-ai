"""Security utilities for the ReviewOps AI backend.

Currently limited to GitHub webhook HMAC-SHA256 signature verification.
"""

import hashlib
import hmac
import logging

logger = logging.getLogger(__name__)


def verify_github_signature(
    payload_body: bytes,
    signature_header: str,
    secret: str,
) -> bool:
    """Validate a GitHub webhook payload against its X-Hub-Signature-256.

    Args:
        payload_body: Raw request body bytes.
        signature_header: Value of the ``X-Hub-Signature-256`` header
            (format: ``sha256=<hex>``).
        secret: The shared webhook secret configured in the GitHub App.

    Returns:
        ``True`` if the signature is valid, ``False`` otherwise.
    """
    if not signature_header or not signature_header.startswith("sha256="):
        logger.warning("Missing or malformed signature header")
        return False

    expected_signature = (
        "sha256="
        + hmac.new(
            secret.encode("utf-8"),
            payload_body,
            hashlib.sha256,
        ).hexdigest()
    )

    is_valid: bool = hmac.compare_digest(expected_signature, signature_header)
    if not is_valid:
        logger.warning("GitHub webhook signature mismatch")
    return is_valid
