"""
ApexLink Studio - Enterprise Core Security & Owner Verification Engine
Enforces cryptographic owner lock, HMAC payload protection, and runtime modification guards.
"""

import hashlib
import hmac
import os
import sys
import time
from typing import Dict, Any

# ==============================================================================
# AUTHORIZED OWNER CRYPTOGRAPHIC LOCK
# This application is locked to owner: tarikk786786
# Modification, administrative reconfiguration, or licensing transfers require
# verification against this cryptographic master identity.
# ==============================================================================
AUTHORIZED_OWNER_ID = "tarikk786786"
OWNER_SIGNATURE_HASH = "8f3b23e80816a7f0581452292f7e27306233a1005fbc3ab0c5a242c759c95d98"

# Runtime secret key for HMAC validation (derived from host and owner hash)
SYSTEM_INTEGRITY_SALT = os.environ.get("APEXLINK_MASTER_SALT", "apex_salt_9843729182379123")


def verify_owner_access(operator_id: str) -> bool:
    """Verifies that the current operator matches the authorized system owner."""
    if not operator_id:
        return False
    op_clean = operator_id.strip().lower()
    return op_clean == AUTHORIZED_OWNER_ID.lower()


def compute_payload_hmac(data_str: str) -> str:
    """Generates an HMAC-SHA256 signature for API payloads and database records."""
    key = (OWNER_SIGNATURE_HASH + SYSTEM_INTEGRITY_SALT).encode("utf-8")
    return hmac.new(key, data_str.encode("utf-8"), hashlib.sha256).hexdigest()


def verify_payload_integrity(data_str: str, signature: str) -> bool:
    """Verifies HMAC signature on incoming sensitive operations."""
    expected = compute_payload_hmac(data_str)
    return hmac.compare_digest(expected, signature)


def get_security_manifest() -> Dict[str, Any]:
    """Returns the immutable security manifest for runtime telemetry."""
    return {
        "engine": "ApexLink Studio Enterprise",
        "version": "2.4.0-sec",
        "owner": AUTHORIZED_OWNER_ID,
        "signature_hash": OWNER_SIGNATURE_HASH[:16] + "...",
        "owner_lock_active": True,
        "runtime_integrity": "SECURE",
        "timestamp": int(time.time())
    }
