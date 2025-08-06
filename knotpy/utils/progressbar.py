import sys
import time
from collections import deque

def _human_time(t):
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
    if t < 5 * 50 * 50:
        return f"{hours}h {minutes}m"
    if t < 2 * 60 * 60 * 24:
        return f"{hours}h"
    if t < 5 * 60 * 60 * 24:
        return f"{days} days {hours}h"
    return f"{days} days"

class bar:
    _blocks = [
        (1.00, "█"), (0.875, "▉"), (0.75, "▊"), (0.625, "▋"),
        (0.5, "▌"), (0.375, "▍"), (0.25, "▎"), (0.125, "▏")
    ]

    BLUE = "\033[0;34m"
    CYAN = "\033[1;35m"
    GRAY = "\033[0;37m"
    RESET = "\033[0m"

    def __init__(self, iterable, total=None, comment=None, width=80, alpha=0.2, update_interval=0.5):
        self.iterable = iterable
        self.total = total if total is not None else len(iterable)
        self.comment = comment
        self.width = width
        self.alpha = alpha
        self.update_interval = update_interval
        self.index = 0
        self.start_time = time.time()
        self.smoothed_speed = None
        self.last_bar_size = 0
        self.last_update_time = self.start_time

        window_len = 50 if 50 < self.total // 10 else max(2, self.total // 10)
        self._history = deque(maxlen=window_len)
        self._history.append((0, self.start_time))

    def set_comment(self, text):
        self.comment = str(text)

    def _progress_bar(self, percent):
        blocks = self.width - 45
        full = int(percent * blocks)
        frac = percent * blocks - full
        bar = "█" * full

        for cutoff, char in self._blocks:
            if frac >= cutoff:
                bar += char
                break
        else:
            if full < blocks:
                bar += "·"

        bar += "·" * (blocks - len(bar))
        return f"|{self.BLUE}{bar}{self.RESET}|"

    def _format_time(self, seconds):
        return "<1s" if seconds < 1 else _human_time(seconds)

    def _update_stats(self):
        now = time.time()
        self._history.append((self.index, now))
        if len(self._history) < 2:
            return

        idx0, t0 = self._history[0]
        idx1, t1 = self._history[-1]
        delta_i = idx1 - idx0
        delta_t = t1 - t0

        raw_speed = delta_i / delta_t if delta_t > 0 else None
        if raw_speed is not None:
            if self.smoothed_speed is None:
                self.smoothed_speed = raw_speed
            else:
                self.smoothed_speed = (
                    self.alpha * raw_speed + (1 - self.alpha) * self.smoothed_speed
                )

    def _print_progress(self):
        percent = self.index / self.total
        speed = self.smoothed_speed if self.smoothed_speed else 0.00001
        eta = (self.total - self.index) / speed if speed > 0 else float('inf')
        it_speed = f"{speed:.1f} it/s"

        bar_str = self._progress_bar(percent)
        pct_str = f"{percent * 100:5.1f}%"
        eta_str = f"{self.BLUE}{self._format_time(eta)}{self.RESET}"
        speed_str = f"{self.CYAN}{it_speed}{self.RESET}"
        count_str = f"{self.GRAY}{self.index}/{self.total}{self.RESET}"
        comment_str = f" ({self.comment})" if self.comment else ""

        output = f"\r{bar_str} {pct_str} eta {eta_str} {speed_str}{comment_str} {count_str}"
        output += " " * (self.last_bar_size - len(output))
        self.last_bar_size = len(output)

        sys.stdout.write(output)
        sys.stdout.flush()

    def __iter__(self):
        for item in self.iterable:
            yield item
            self.index += 1
            self._update_stats()

            now = time.time()
            if now - self.last_update_time >= self.update_interval or self.index == self.total:
                self._print_progress()
                self.last_update_time = now
        sys.stdout.write("\n")

# #
#
#
#
#
# class _MultiProgressBar:
#     def __init__(self, total):
#         self.total = []  # total iterations
#         self.current = []  # current progress
#         self.comment = ""
#         self.start_time = time.time()
#         self.last_output = ""
#         self.all_ticks = 0
#
#         # history
#         self.last_tick_time = None
#         self.last_frac = None
#         self.last_eta = None
#         self.last_bar_update = None
#
#         self.add_another_bar(total)
#
#     def tick(self, no_stats=False):
#         """updates last level of the bar"""
#         self.all_ticks += 1
#         self.current[-1] += 1
#         N = len(self.total)  # number of bars
#         L = round((_PROGRESS_BAR_LENGTH - N + 1) / N)  # length of one bar
#
#         # compute fractions of bars (0 = 0%, 1 = 100%), evaluate fractions based on inner levels
#         frac = [0.0] * N
#         frac[-1] = min(1.0, (self.current[-1] + 1) / self.total[-1])  # looks nicer with 1 additional bar
#         for i in reversed(range(len(self.total)-1)):
#             frac[i] = min(1.0, (self.current[i] + (frac[i + 1] if i < N - 1 else 0.0)) / self.total[i])
#
#         full = [int(L * f) for f in frac]
#         reminder = [int(L * f * 8) % 8 for f in frac]
#
#
#         # compute bar lengths
#         s_bars = [""] * N
#         for i in range(N):
#             s_bars[i] = _unicode_blocks[-1] * full[i]
#             if reminder[i]:
#                 s_bars[i] += _unicode_blocks[reminder[i]]
#             s_bars[i] = _bar_colors[i%len(_bar_colors)] + s_bars[i] + _dot_colors[i%len(_bar_colors)] + _unicode_blocks[0] * (L - len(s_bars[i])) + "\033[0m"
#
#
#         # percentage & comment
#         s_percentage = f"{(100*frac[0]):.1f}%"
#         s_comment = ("(" + self.comment + ")") if self.comment else ""
#         current_time = time.time()
#         dt = current_time - self.start_time
#
#         #compute ETA
#         if self.last_tick_time is None:
#             ticks_per_second = 0.0
#             eta = (dt / frac[0] - dt) if frac[0] > 0 else float("inf")
#             s_eta = _human_time(eta)
#             tick_time = 0
#         else:
#             tick_time = current_time - self.last_tick_time
#             ticks_per_second = (round(1/tick_time) if 1/tick_time > 10 else round(1/tick_time, 2)) if tick_time != 0 else float("inf")
#
#             delta_frac = frac[0] - self.last_frac[0]
#             iteration_eta = (1.0 - frac[0]) * tick_time / delta_frac if delta_frac != 0 else float("inf")
#             eta = (self.last_eta + iteration_eta) * 0.5
#             s_eta = _human_time(iteration_eta)
#
#
#
#         eta = (dt / frac[0] - dt) if frac[0] else 0
#         s_eta = _human_time(eta)
#
#         self.last_eta = eta
#         self.last_tick_time = current_time
#         self.last_frac = frac
#
#
#         # #####
#         #     #eta = _human_time(dt / frac[0] - dt) if frac[0] > 0 else "∞"
#         #
#         # if self.last_tick_time is None:
#         #     ticks_per_second = 0
#         #
#         # else:
#         #
#         #     # compute iterations per second based only on latest iteration
#         #     #s_eta_whole = _human_time(dt / frac[0] - dt) if frac[0] > 0 else "∞"
#         #
#         #     # compute ETA based on current iteration
#         #     delta_frac = frac[0] - self.last_frac[0]
#         #     iteration_eta = (1.0 - frac[0]) * tick_time / delta_frac if delta_frac != 0 else "∞"
#         #
#         #     iteration_eta = (iteration_eta + self.last_iteration_eta) * 0.5
#         #     self.last_iteration_eta = iteration_eta
#         #     self.last_frac0 = frac[0]
#         #     s_eta = _human_time(iteration_eta)
#
#         if self.last_bar_update is None or (current_time - self.last_bar_update >= 0.1) or any(f > 0.99 for f in frac):
#
#             self.last_bar_update = current_time
#
#             s_output = "\r|" + "|".join(s_bars) + f"| "
#             s_output += f"{s_percentage} \033[0;34meta {s_eta} \033[0;35m{ticks_per_second} it/s"
#             if s_comment:
#                 s_output += f"\033[0m {s_comment}"
#             s_output += f" \033[0;37m{self.current[0]+1}/{self.total[0]}\033[0m"
#             if s_output != self.last_output:
#                 sys.stdout.write(s_output)
#                 self.last_output = s_output
#
#             sys.stdout.flush()
#
#     def add_another_bar(self, total):
#         self.total.append(total if total else 1)
#         self.current.append(-1)
#
#     def remove_bar(self):
#         #self.tick()
#         del self.total[-1]
#         del self.current[-1]
#
#         # clean up if it is the last bar
#         if not len(self.total):
#             sys.stdout.write('\n')
#             sys.stdout.flush()
#             self.all_ticks = 0
#
#
#
# class Bar:
#     # TODO: updates before task, should maybe start at -1?  and update also at StopIteration.
#     def __init__(self, iterable, total=None, comment=None):
#
#         global _global_progress_bar
#
#         if _global_progress_bar is None:
#             _global_progress_bar = _MultiProgressBar(total or len(iterable))
#             _global_progress_bar.comment = comment or ""
#         else:
#             _global_progress_bar.add_another_bar(total or len(iterable))
#         self.iterable =iterable
#
#     @staticmethod
#     def set_comment(comment):
#         global _global_progress_bar
#         if _global_progress_bar is not None:
#             _global_progress_bar.comment = comment
#
#     @staticmethod
#     def reset():
#         global _global_progress_bar
#         _global_progress_bar = None
#
#     def __iter__(self):
#         self.iter = iter(self.iterable)
#         return self
#
#     def __next__(self):
#         global _global_progress_bar
#         try:
#             next_item = next(self.iter)
#             _global_progress_bar.tick()
#             return next_item
#         except StopIteration:
#             _global_progress_bar.remove_bar()
#             raise StopIteration
#
#
#
# # Example usage
# if __name__ == "__main__":
#
#
#
#
#     for b in Bar(list(range(10))):
#         for c in Bar(list(range(5))):
#             for d in Bar(list(range(10))):
#                 Bar.set_comment("hey there")
#
#                 time.sleep(0.5)
#
#     # for b in Bar(list(range(3))):
#     #     for c in Bar(list(range(5))):
#     #             Bar.set_comment("hey there")
#     #             sleep(0.1)
#     #
#     # for b in Bar(list(range(3))):
#     #     Bar.set_comment("hey there")
#     #     sleep(1)
#     #
#     #
#     # for b in Bar(list(range(3))):
#     #     for c in Bar(list(range(5))):
#     #         for d in Bar(list(range(10))):
#     #             for e in Bar(list(range(2))):
#     #                 Bar.set_comment("hey there")
#     #                 sleep(0.01)
#
#
#     for b in Bar(list(range(3))):
#         for c in Bar(list(range(5))):
#             for d in Bar(list(range(10))):
#                 for e in Bar(list(range(2))):
#                     for f in Bar(list(range(2))):
#
#                         Bar.set_comment("hey there")
#                         time.sleep(0.01)
#
#     for b in Bar(list(range(3))):
#         for c in Bar(list(range(5))):
#             for d in Bar(list(range(10))):
#                 for e in Bar(list(range(2))):
#                     for f in Bar(list(range(2))):
#                         for e1 in Bar(list(range(2))):
#                             for f2 in Bar(list(range(2))):
#                                 Bar.set_comment("hey there")
#                                 time.sleep(0.01)
#
#
#     exit()
#
#     progress_bar = ProgressBar(4)
#
#     for i in range(4):
#         progress_bar.update()
#         sleep(2)  # Simulate some work being done
#     progress_bar.finish()
#     exit()
#
#
#     total_steps = 10
#     progress_bar = ProgressBar(total_steps)
#
#     for i in range(total_steps + 1):
#         progress_bar.update()
#         progress_bar.add_inner_bar(100)
#         for j in range(100):
#             progress_bar.update(1)
#             time.sleep(0.01)  # Simulate some work being done
#
#         progress_bar.pop()
#
#     progress_bar.finish()
#
#
# class FakeBar:
#     """ empty bar, does nothing"""
#     def __init__(self, iterable, total=None):
#         self.iterable = iterable
#     def __iter__(self):
#         return iter(self.iterable)
#     @staticmethod
#     def set_comment(_):
#         pass
#
#
#
# class ProgressTracker:
#     COLORS = [
#         "\033[91m",  # Red
#         "\033[92m",  # Green
#         "\033[93m",  # Yellow
#         "\033[94m",  # Blue
#         "\033[95m",  # Magenta
#         "\033[96m",  # Cyan
#     ]
#     RESET = "\033[0m"
#
#     def __init__(self, *labels):
#         self.labels = labels
#
#     def update(self, *values):
#         if len(values) != len(self.labels):
#             raise ValueError("Number of values must match number of labels")
#         parts = []
#         for i, (label, value) in enumerate(zip(self.labels, values)):
#             color = self.COLORS[i % len(self.COLORS)]
#             parts.append(f"{color}{label}: {value}{self.RESET}")
#         print("\r" + " | ".join(parts), end="", flush=True)
#
#     def finish(self):
#         print("\r" + " " * 120 + "\r", end="", flush=True)

if __name__ == "__main__":
    for b in bar(list(range(123))):
        time.sleep(0.1)
# for b in Bar(list(range(3))):
    #     for c in Bar(list(range(5))):
    #             Bar.set_comment("hey there")
    #             sleep(0.1)