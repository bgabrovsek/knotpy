"""
Provides an in-memory dictionary-style cache for intermediate storage in KnotPy.

This cache limits the number of entries and key lengths, and replaces the longest key when full.
Designed for fast, dependency-free use in performance-sensitive contexts.
"""

from __future__ import annotations

from typing import Any, Hashable

__all__ = ["Cache"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovšek@pef.uni-lj.si>"


class Cache(dict[Hashable, Any]):
    """In-memory bounded-size cache for key-value pairs with limited key lengths.

    This cache:
      - Limits the total number of items (``max_cache_size``).
      - Skips keys whose length (``len(key)``) exceeds ``max_key_length``.
      - When full, evicts the entry with the **longest key** if the incoming key is **shorter**.

    Notes:
        - Keys must be hashable. If a key has no length (i.e., ``len(key)`` raises ``TypeError``),
          it is ignored (not cached).
        - Updating an existing key always succeeds (no eviction), even when the cache is full.

    Example:
        >>> cache = Cache(max_cache_size=3, max_key_length=5)
        >>> cache['abc'] = 1
        >>> cache['def'] = 2
        >>> cache['ghi'] = 3
        >>> cache['abcdef'] = 4  # ignored: key too long
        >>> list(cache.items())
        [('abc', 1), ('def', 2), ('ghi', 3)]

    Attributes:
        max_cache_size (int): Maximum number of entries the cache can hold (<=0 disables caching).
        max_key_length (int): Maximum allowed length of any key.
    """

    def __init__(self, max_cache_size: int, max_key_length: int) -> None:
        """Initialize the cache.

        Args:
            max_cache_size: Maximum entries to retain; if <= 0, all insertions are ignored.
            max_key_length: Maximum allowed length of any key.
        """
        super().__init__()
        self.max_cache_size = int(max_cache_size)
        self.max_key_length = int(max_key_length)

    def __setitem__(self, key: Hashable, value: Any) -> None:
        """Insert or update an item, applying capacity and key-length rules.

        Behavior:
            - If ``max_cache_size <= 0`` → do nothing.
            - If key lacks ``len`` → ignore.
            - If ``len(key) > max_key_length`` → ignore.
            - If key already exists → update in-place.
            - If under capacity → insert.
            - If at capacity → evict the **longest** existing key **only if**
              the new key is strictly shorter; otherwise ignore.

        Args:
            key: Hashable key.
            value: Value to store.
        """
        # Caching disabled
        if self.max_cache_size <= 0:
            return

        # Keys without a length are ignored
        try:
            key_len = len(key)  # type: ignore[arg-type]
        except TypeError:
            return

        # Ignore too-long keys
        if key_len > self.max_key_length:
            return

        # Update existing key regardless of capacity
        if key in self:
            super().__setitem__(key, value)
            return

        # Insert if there is room
        if len(self) < self.max_cache_size:
            super().__setitem__(key, value)
            return

        # Cache full: find the longest existing key
        longest_key: Hashable | None = None
        longest_len = -1

        for existing_key in self.keys():
            try:
                existing_len = len(existing_key)  # type: ignore[arg-type]
            except TypeError:
                # If an existing key has no length, treat it as "infinitely long" so it is preferred for eviction.
                existing_len = float("inf")
            if existing_len > longest_len:
                longest_len = existing_len
                longest_key = existing_key

        # Replace only if new key is strictly shorter
        if key_len < longest_len and longest_key is not None:
            # Use dict.pop to avoid recursive __delitem__ logic
            self.pop(longest_key, None)
            super().__setitem__(key, value)
        # else: drop the new item silently

    # Optional: explicit helper (kept private; useful if policy changes later)
    def _longest_key(self) -> Hashable | None:
        """Return the current longest key (by ``len``), or ``None`` if empty.

        Returns:
            The key with the maximum length among present keys, or ``None`` if empty.

        Note:
            Keys without ``len`` are treated as having infinite length.
        """
        if not self:
            return None
        longest_key: Hashable | None = None
        longest_len = -1
        for k in self.keys():
            try:
                k_len = len(k)  # type: ignore[arg-type]
            except TypeError:
                k_len = float("inf")
            if k_len > longest_len:
                longest_len = k_len
                longest_key = k
        return longest_key


if __name__ == "__main__":
    pass
