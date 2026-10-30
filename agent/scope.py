"""Scope control.

This is the single most important file in the project and the main ethics
lesson of the workshop: the agent can *decide* what to test, but it can never
*choose where*. The host is fixed from config, and every tool validates any
model-supplied URL against this allowlist before doing anything.

Combined with the network egress lock on the lab subnet (see deploy/), this is
what keeps an autonomous agent from ever reaching a system it isn't authorized
to touch.
"""

from urllib.parse import urlparse

from . import config

ALLOWED_HOSTS = {config.TARGET_HOST}


class OutOfScope(Exception):
    pass


def host_of(url_or_path: str) -> str:
    """Resolve a model-supplied value to a hostname.

    A bare path like '/login' is assumed to be on the target. A full URL has
    its host checked. Anything else is rejected."""
    if url_or_path.startswith("/"):
        return config.TARGET_HOST
    parsed = urlparse(url_or_path)
    if not parsed.hostname:
        # Not a path, not a URL we can parse -> refuse.
        raise OutOfScope(f"Cannot determine host for {url_or_path!r}")
    return parsed.hostname


def assert_in_scope(url_or_path: str) -> None:
    host = host_of(url_or_path)
    if host not in ALLOWED_HOSTS:
        raise OutOfScope(
            f"Refusing: {host!r} is out of scope. "
            f"This engagement is limited to {sorted(ALLOWED_HOSTS)}."
        )


def target_url(path: str = "/") -> str:
    """Build an in-scope URL from a path the model proposed."""
    if not path.startswith("/"):
        path = "/" + path
    assert_in_scope(path)
    return config.TARGET_URL + path
