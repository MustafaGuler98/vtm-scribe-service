import math
import threading
import time
from dataclasses import dataclass
from typing import Dict

from fastapi import Request


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    retry_after_seconds: int


@dataclass
class _RateLimitWindow:
    started_at: float
    request_count: int


class FixedWindowRateLimiter:
    def __init__(
        self,
        permit_limit: int,
        window_seconds: int,
        cleanup_interval_seconds: int = 60,
    ) -> None:
        if permit_limit <= 0:
            raise ValueError("permit_limit must be greater than zero")

        if window_seconds <= 0:
            raise ValueError("window_seconds must be greater than zero")

        if cleanup_interval_seconds <= 0:
            raise ValueError("cleanup_interval_seconds must be greater than zero")

        self._permit_limit = permit_limit
        self._window_seconds = window_seconds
        self._cleanup_interval_seconds = cleanup_interval_seconds
        self._windows: Dict[str, _RateLimitWindow] = {}
        self._lock = threading.Lock()
        self._next_cleanup_at = time.monotonic() + cleanup_interval_seconds

    def try_acquire(self, key: str) -> RateLimitDecision:
        now = time.monotonic()

        with self._lock:
            self._remove_expired_windows(now)

            current_window = self._windows.get(key)
            if (
                current_window is None
                or now - current_window.started_at >= self._window_seconds
            ):
                self._windows[key] = _RateLimitWindow(
                    started_at=now,
                    request_count=1,
                )
                return RateLimitDecision(allowed=True, retry_after_seconds=0)

            if current_window.request_count >= self._permit_limit:
                retry_after_seconds = max(
                    1,
                    math.ceil(
                        current_window.started_at + self._window_seconds - now
                    ),
                )
                return RateLimitDecision(
                    allowed=False,
                    retry_after_seconds=retry_after_seconds,
                )

            current_window.request_count += 1
            return RateLimitDecision(allowed=True, retry_after_seconds=0)

    def _remove_expired_windows(self, now: float) -> None:
        if now < self._next_cleanup_at:
            return

        # Cleanup is performed while holding the same lock so concurrent requests
        # cannot revive or update a window while it is being removed.
        expired_keys = [
            key
            for key, window in self._windows.items()
            if now - window.started_at >= self._window_seconds
        ]
        for key in expired_keys:
            del self._windows[key]

        self._next_cleanup_at = now + self._cleanup_interval_seconds


def resolve_client_ip(request: Request) -> str:
    # Vercel owns these headers in production, preventing callers from choosing
    # a different rate-limit bucket by supplying a spoofed client address.
    for header_name in ("x-vercel-forwarded-for", "x-forwarded-for"):
        forwarded_for = request.headers.get(header_name)
        if forwarded_for:
            client_ip = forwarded_for.split(",", maxsplit=1)[0].strip()
            if client_ip:
                return client_ip

    if request.client is not None:
        return request.client.host

    return "unknown"
