import os
import secrets
from typing import Optional

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")

# In-memory session store (resets on restart — fine for a single-process app)
_sessions: set = set()


def login(username: str, password: str) -> Optional[str]:
    """Verify credentials and return a session token, or None on failure."""
    ok = (
        secrets.compare_digest(username, ADMIN_USERNAME)
        and secrets.compare_digest(password, ADMIN_PASSWORD)
    )
    if not ok:
        return None
    token = secrets.token_urlsafe(32)
    _sessions.add(token)
    return token


def is_authenticated(token: Optional[str]) -> bool:
    return bool(token and token in _sessions)


def logout(token: Optional[str]) -> None:
    if token:
        _sessions.discard(token)
