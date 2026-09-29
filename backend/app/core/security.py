"""
VELLAM Geospatial Platform - Core Security
Provides secure, timing-attack-resistant cryptographic verification for administrative operations.
"""

import secrets
from app.core.config import settings


def verify_admin_key(candidate_key: str) -> bool:
    """
    Verify the administrator secret key using constant-time string comparison
    to protect against timing-attack vulnerabilities.
    """
    if not candidate_key:
        return False

    clean_candidate = candidate_key.strip()
    target_key = settings.ADMIN_SECRET_KEY.strip()

    return secrets.compare_digest(clean_candidate, target_key)
