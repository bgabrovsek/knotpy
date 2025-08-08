"""
Lightweight text progress bar for terminal loops, with tick() and multiprocessing support.

- Works as an iterator OR as a manual progress meter via tick().
- For multiprocessing, pass a multiprocessing.Value('i') as shared_counter and call tick()
  from workers; the bar in the main process will display shared progress.

Example (iterator):
    >>> from time import sleep
    >>> for _ in bar(range(100), comment="processing"):
    ...     sleep(0.01)

Example (manual tick):
    >>> pb = bar(total=100, comment="manual")
    >>> for _ in range(100):
    ...     pb.tick()
    ... pb.refresh()  # final refresh if needed

Example (multiprocessing):
    >>> import multiprocessing as mp, time
    >>> total = 200
    >>> counter = mp.Value('i', 0)
    >>> def work(counter):
    ...     for _ in range(50):
    ...         time.sleep(0.01)
    ...         with counter.get_lock():
    ...             counter.value += 1
    >>> procs = [mp.Process(target=work, args=(counter,)) for _ in range(4)]
    >>> for p in procs: p.start()
    >>> pb = bar(total=total, shared_counter=counter, comment="mp")
    >>> while any(p.is_alive() for p in procs):
    ...     pb.refresh()  # updates display based on shared counter
    ...     time.sleep(0.05)
    >>> for p in procs: p.join()
    >>> pb.refresh()  # final refresh
"""

from __future__ import annotations

import sys
import time
from collections import deque
from typing import Deque, Iterable, Iterator, Optional, Tuple, TypeVar, Any

__all__ = ["ProgressBar", "bar"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

T = TypeVar("T")


def _human_time(t: float) -> str:
    """Format seconds into a short human string."""
    if t == float("inf"):
        return "∞"
    t = int(t)
    seconds = t % 60
    minutes = (t // 60) % 60
    hours = (t // 3600) % 24
    days = (t // 86400)

    if t < 2 * 60:
        return f"{minutes * 60 + seconds}s"
    if t < 5 * 60:
        return f"{minutes}m {seconds}s"
    if t < 2 * 60 * 60:
        return f"{hours * 60 + minutes}m"
    if t < 5 * 60 * 60:  # fixed bug: was 5*50*50
        return f"{hours}h {minutes}m"
    if t < 2 * 60 * 60 * 24:
        return f"{hours}h"
    if t < 5 * 60 * 60 * 24:
        return f"{days} days {hours}h"
    return f"{days} days"


class ProgressBar(Iterator[T]):
    """A simple terminal progress bar.

    Args:
        iterable: Any iterable to consume. If omitted, you can drive progress via `tick()`.
        total: Total number of items (required for manual / shared-counter modes).
        comment: Optional right-side comment (changes at runtime via :meth:`set_comment`).
        width: Total character width of the bar line.
        alpha: Smoothing factor for EMA speed (0..1).
        update_interval: Minimum seconds between screen updates.
        shared_counter: Optional multiprocessing.Value('i') (or duck with `.value` and `.get_lock()`).
                        If provided, the bar will display this shared counter.
                        You can call `tick()` from workers or just mutate `shared_counter.value`.

    Notes:
        - If `iterable` is None, `total` must be provided.
        - To use in multiprocessing, keep the bar in the main process and update shared_counter from workers.
          Call `refresh()` periodically in the main process to redraw.
    """

    _blocks: Tuple[Tuple[float, str], ...] = (
        (1.00, "█"), (0.875, "▉"), (0.75, "▊"), (0.625, "▋"),
        (0.5, "▌"), (0.375, "▍"), (0.25, "▎"), (0.125, "▏"),
    )

    BLUE = "\033[0;34m"
    CYAN = "\033[1;35m"
    GRAY = "\033[0;37m"
    RESET = "\033[0m"

    def __init__(
        self,
        iterable: Optional[Iterable[T]] = None,
        *,
        total: Optional[int] = None,
        comment: Optional[str] = None,
        width: int = 80,
        alpha: float = 0.2,
        update_interval: float = 0.5,
        shared_counter: Any = None,
    ) -> None:
        self.iterable = iter(iterable) if iterable is not None else None

        # Resolve total
        if total is None and iterable is not None:
            try:
                total = len(iterable)  # type: ignore[arg-type]
            except Exception:
                raise TypeError("ProgressBar: 'total' required for iterables without __len__ or when iterable=None.")
        if total is None:
            raise TypeError("ProgressBar: 'total' must be provided.")
        self.total: int = max(0, int(total))

        self.comment: Optional[str] = comment
        self.width: int = max(20, int(width))
        self.alpha: float = float(alpha)
        self.update_interval: float = float(update_interval)

        # Internal counter (used if no shared_counter)
        self.index: int = 0

        # Optional shared counter (multiprocessing.Value or similar)
        self._shared = shared_counter
        self._use_shared = shared_counter is not None

        self.start_time: float = time.time()
        self.smoothed_speed: Optional[float] = None
        self.last_bar_size: int = 0
        self.last_update_time: float = self.start_time

        # Keep a small window of (index, time) for raw speed estimation
        window_len = max(2, min(50, (self.total // 10) or 10))
        self._history: Deque[Tuple[int, float]] = deque(maxlen=window_len)
        self._history.append((0, self.start_time))

    # Public API

    def set_comment(self, text: Optional[str]) -> None:
        """Set/clear the comment displayed on the right side of the bar."""
        self.comment = None if text is None else str(text)

    def tick(self, n: int = 1) -> None:
        """Increment progress by `n` and maybe redraw (throttled by update_interval)."""
        if self._use_shared:
            # increment shared counter safely if it exposes a lock
            lock = getattr(self._shared, "get_lock", None)
            if callable(lock):
                with self._shared.get_lock():
                    self._shared.value += n
            else:
                # best effort (not strictly safe)
                self._shared.value += n
        else:
            self.index += n

        self._update_stats()
        self._maybe_print()

    def refresh(self) -> None:
        """Force a redraw (useful in multiprocessing main loop)."""
        self._update_stats()
        self._print_progress()

    # Internal helpers

    def _current_index(self) -> int:
        if self._use_shared:
            return int(self._shared.value)
        return self.index

    def _progress_bar(self, percent: float) -> str:
        # Reserve right side text; use the rest for blocks
        blocks = max(1, self.width - 45)
        full = int(percent * blocks)
        frac = percent * blocks - full
        s = "█" * full

        # fractional block
        for cutoff, ch in self._blocks:
            if frac >= cutoff:
                s += ch
                break
        else:
            if full < blocks:
                s += "·"

        s += "·" * (blocks - len(s))
        return f"|{self.BLUE}{s}{self.RESET}|"

    def _format_time(self, seconds: float) -> str:
        return "<1s" if seconds < 1 else _human_time(seconds)

    def _update_stats(self) -> None:
        now = time.time()
        idx = self._current_index()
        self._history.append((idx, now))
        if len(self._history) < 2:
            return

        idx0, t0 = self._history[0]
        idx1, t1 = self._history[-1]
        delta_i = idx1 - idx0
        delta_t = t1 - t0

        if delta_t <= 0:
            return

        raw_speed = delta_i / delta_t
        if self.smoothed_speed is None:
            self.smoothed_speed = raw_speed
        else:
            self.smoothed_speed = self.alpha * raw_speed + (1 - self.alpha) * self.smoothed_speed

    def _maybe_print(self) -> None:
        now = time.time()
        if now - self.last_update_time >= self.update_interval or self._current_index() >= self.total:
            self._print_progress()
            self.last_update_time = now

    def _print_progress(self) -> None:
        idx = self._current_index()
        percent = 1.0 if self.total == 0 else min(1.0, idx / max(1, self.total))
        speed = self.smoothed_speed or 0.0
        eta = (self.total - idx) / speed if speed > 0 else float("inf")
        it_speed = f"{speed:.1f} it/s"

        bar_str = self._progress_bar(percent)
        pct_str = f"{percent * 100:5.1f}%"
        eta_str = f"{self.BLUE}{self._format_time(eta)}{self.RESET}"
        speed_str = f"{self.CYAN}{it_speed}{self.RESET}"
        count_str = f"{self.GRAY}{idx}/{self.total}{self.RESET}"
        comment_str = f" ({self.comment})" if self.comment else ""

        output = f"\r{bar_str} {pct_str} eta {eta_str} {speed_str}{comment_str} {count_str}"
        # pad to clear previous longer line
        output += " " * max(0, self.last_bar_size - len(output))
        self.last_bar_size = len(output)

        sys.stdout.write(output)
        sys.stdout.flush()

        if idx >= self.total:
            sys.stdout.write("\n")
            sys.stdout.flush()

    # Iterator protocol

    def __iter__(self) -> "ProgressBar[T]":
        if self.iterable is None:
            raise TypeError("ProgressBar: no iterable provided; use tick() or pass an iterable.")
        return self

    def __next__(self) -> T:
        if self.iterable is None:
            raise StopIteration
        item = next(self.iterable)  # can raise StopIteration
        self.index += 1
        self._update_stats()
        self._maybe_print()
        return item


# Backward-compatible alias
bar = ProgressBar
