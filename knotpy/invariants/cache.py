# knotpy/invariants/cache.py
"""
Lightweight LFU cache with an optional size cap.

Notes:
    - Only keys with ``len(key) <= max_number_of_nodes`` are cached.
    - On cache miss, :meth:`get` returns ``None`` (even if a cached value could be ``None``).
      If you need to distinguish, wrap your values or add a sentinel in the caller.

This is intentionally minimal; O(n) eviction via a linear scan is acceptable for small caches.
"""

from __future__ import annotations

from collections.abc import Sized
from typing import TypeVar, Generic, Protocol, runtime_checkable

__all__ = ["Cache"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"


@runtime_checkable
class _Hashable(Protocol):
    def __hash__(self) -> int: ...


@runtime_checkable
class HashableSized(_Hashable, Sized, Protocol):
    """Protocol for keys that are both hashable and have a length."""


K = TypeVar("K", bound=HashableSized)
V = TypeVar("V")


class Cache(Generic[K, V]):
    """Least-frequently-used (LFU) cache with an optional capacity.

    Args:
        max_number_of_nodes: Only cache keys with ``len(key) <= max_number_of_nodes``.
        cache_size: Maximum number of entries to keep. If ``None``, the cache grows without limit.

    Attributes:
        cache_size: The capacity limit or ``None``.
        max_number_of_nodes: Maximum allowed ``len(key)`` to be cached.

    Notes:
        - Eviction policy is LFU using a simple usage counter. Tie-breaking is arbitrary.
        - Updating an existing key bumps its usage counter by 1 (preserves your original behavior).
    """

    def __init__(self, max_number_of_nodes: int, cache_size: int | None = None) -> None:
        self.cache_size = cache_size
        self.cache: dict[K, V] = {}
        self.usage_count: dict[K, int] = {}
        self.max_number_of_nodes = max_number_of_nodes

    def get(self, key: K) -> V | None:
        """Return the cached value for ``key`` and increment its usage, or ``None`` if missing."""
        if key in self.cache:
            self.usage_count[key] += 1
            return self.cache[key]
        return None

    def set(self, key: K, value: V) -> None:
        """Insert or update ``key`` with ``value``, enforcing LFU eviction if at capacity.

        Keys with ``len(key) > max_number_of_nodes`` are ignored (not cached).
        """
        # Respect length cap
        if len(key) > self.max_number_of_nodes:
            return

        if key in self.cache:
            self.cache[key] = value
            self.usage_count[key] += 1
            return

        # Evict if needed
        if self.cache_size is not None and len(self.cache) >= self.cache_size:
            # Least frequently used key (O(n) scan)
            least_frequent_key = min(self.usage_count, key=self.usage_count.get)
            del self.cache[least_frequent_key]
            del self.usage_count[least_frequent_key]

        self.cache[key] = value
        self.usage_count[key] = 1

    # Small quality-of-life helpers (don’t change existing API)
    def __contains__(self, key: K) -> bool:
        return key in self.cache

    def __len__(self) -> int:
        return len(self.cache)

    def clear(self) -> None:
        """Remove all entries."""
        self.cache.clear()
        self.usage_count.clear()


if __name__ == "__main__":
    pass
