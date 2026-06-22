"""Shared HTTP helpers: fetch with retries, provenance, and a clear signal
when an outbound host is blocked by the execution environment.

Every fetch records URL, the host that actually served the bytes, an HTTP
status, and a timestamp so SOURCES.json and the validation report can carry
full provenance. A blocked host raises FetchBlocked rather than returning a
misleading 403 body.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests

USER_AGENT = (
    "publicreform-pipeline/1.0 (research dashboard; contact via repo) "
    "python-requests"
)

DEFAULT_TIMEOUT = 30
DEFAULT_RETRIES = 4


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class FetchResult:
    """Outcome of a single fetch attempt, blocked or successful."""

    url: str
    host: str
    status: int | None
    fetched_at: str
    blocked: bool = False
    deny_reason: str | None = None
    content: bytes | None = field(default=None, repr=False)

    @property
    def ok(self) -> bool:
        return not self.blocked and self.status is not None and 200 <= self.status < 300


class FetchBlocked(RuntimeError):
    """Raised when the environment network policy denies an outbound host.

    Detected via the proxy deny header (x-deny-reason: host_not_allowed) or a
    403 with no body served by the policy layer rather than the origin.
    """

    def __init__(self, url: str, host: str, deny_reason: str):
        self.url = url
        self.host = host
        self.deny_reason = deny_reason
        super().__init__(
            f"host blocked by environment network policy: {host} "
            f"({deny_reason}); url={url}"
        )


def _host_of(url: str) -> str:
    return urlparse(url).netloc


def fetch(
    url: str,
    *,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
    allow_redirects: bool = True,
) -> FetchResult:
    """GET a URL with bounded retries and backoff.

    Returns a FetchResult on success. Raises FetchBlocked when the network
    policy denies the host (no point retrying a policy denial). Retries only
    transient transport errors and 5xx responses.
    """
    host = _host_of(url)
    last_status: int | None = None
    backoff = 2
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(
                url,
                headers={"User-Agent": USER_AGENT},
                timeout=timeout,
                allow_redirects=allow_redirects,
            )
        except requests.RequestException:
            if attempt == retries:
                return FetchResult(
                    url=url,
                    host=host,
                    status=None,
                    fetched_at=utc_now_iso(),
                    blocked=False,
                    deny_reason="transport_error",
                )
            time.sleep(backoff)
            backoff *= 2
            continue

        deny_reason = resp.headers.get("x-deny-reason")
        if deny_reason or (resp.status_code == 403 and not resp.content):
            raise FetchBlocked(url, host, deny_reason or "forbidden_no_body")

        last_status = resp.status_code
        if resp.status_code >= 500 and attempt < retries:
            time.sleep(backoff)
            backoff *= 2
            continue

        served_host = _host_of(resp.url) or host
        return FetchResult(
            url=url,
            host=served_host,
            status=resp.status_code,
            fetched_at=utc_now_iso(),
            content=resp.content,
        )

    return FetchResult(
        url=url, host=host, status=last_status, fetched_at=utc_now_iso()
    )
