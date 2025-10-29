from __future__ import annotations

import csv
from pathlib import Path
import gzip
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Callable, Iterable

from tqdm import tqdm
from knotpy.notation.native import to_knotpy_notation

# --- Globals initialized in each worker process --------------------------------

_LOCK: mp.synchronize.Lock | None = None
_FILENAME: str | None = None
_FIELDNAMES: list[str] | None = None
_INVARIANTS: dict[str, Callable] | None = None


def _is_gz(path: str | Path) -> bool:
    return str(path).endswith(".gz")


def _open_text(path: str | Path, mode: str):
    """
    Open text file or gzipped text file based on suffix.
    mode: 'w'/'a' (plain) or 'wt'/'at' (gz) will be normalized automatically.
    """
    path = str(path)
    if _is_gz(path):
        # normalize to text modes for gzip
        if "b" in mode:
            mode = mode.replace("b", "")
        if "t" not in mode:
            mode = mode + "t"
        return gzip.open(path, mode=mode, encoding="utf-8", newline="")
    # plain text
    # ensure no 't' flag for built-in open (it's the default)
    mode = mode.replace("t", "")
    return open(path, mode=mode, encoding="utf-8", newline="")


def _init_worker(
    lock: mp.synchronize.Lock,
    filename: str,
    fieldnames: list[str],
    invariants: dict[str, Callable],
) -> None:
    """
    Per-process initializer for worker state. Stores shared objects in module globals
    so each forked process can access them without re-pickling on every task.
    """
    global _LOCK, _FILENAME, _FIELDNAMES, _INVARIANTS
    _LOCK = lock
    _FILENAME = filename
    _FIELDNAMES = fieldnames
    _INVARIANTS = invariants


def _compute_and_write_row(diagram) -> tuple[str, list[str]]:
    """
    Compute invariant values for a single diagram and append a CSV row.

    Returns:
        (name, error_messages)
    """
    assert _LOCK is not None and _FILENAME and _FIELDNAMES and _INVARIANTS is not None

    name = getattr(diagram, "name", str(diagram))
    err_msgs: list[str] = []

    # Serialize diagram (best-effort)
    try:
        diag_str = to_knotpy_notation(diagram)
    except Exception as e:
        diag_str = str(diagram)
        err_msgs.append(f"to_knotpy_notation failed for {name}: {e!r}")

    # Compute invariants
    values: dict[str, object] = {}
    for inv_name, inv_fn in _INVARIANTS.items():
        try:
            values[inv_name] = inv_fn(diagram)
        except Exception as e:
            values[inv_name] = None
            err_msgs.append(f"{inv_name} failed for {name}: {e!r}")

    # Append a CSV row (guarded by a lock so writes don’t interleave)
    row = {"name": name, "diagram": diag_str}
    row.update(values)

    print("\n[[", row, "]]\n", flush=True)

    with open("parallel_results.txt", "a", encoding="utf-8") as f:
        f.write(str(row) + "\n")
            
    with _LOCK:
        mode = "at" if _is_gz(_FILENAME) else "a"
        with _open_text(_FILENAME, mode) as f:
            writer = csv.DictWriter(f, fieldnames=_FIELDNAMES)
            writer.writerow(row)

    return name, err_msgs


def save_invariants_parallel(
    filename: str | Path,
    diagrams: Iterable,
    invariants: dict[str, Callable],
    workers: int = 0,
) -> dict[str, list[str]]:
    """
    Compute invariants for many diagrams in parallel and save to CSV (or ``.csv.gz``).

    The output file will contain a header with ``name``, ``diagram``, and one column
    per invariant key in ``invariants``.

    Args:
        filename: Output CSV path (created if missing). Parent dirs will be created.
                  If the name ends with ``.gz``, a gzipped CSV is written.
        diagrams: Iterable of diagram objects. Each should have a ``.name`` or be
                  convertible to ``str(diagram)``.
        invariants: Mapping ``{column_name: callable(diagram) -> value}``.
        workers: Number of worker processes. ``<= 0`` means use ``mp.cpu_count()``.

    Returns:
        dict mapping diagram name -> list of error messages (empty list if none).
    """
    out_path = Path(filename)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["name", "knotpy notation"] + list(invariants.keys())

    # Create/overwrite file and write header
    mode_header = "wt" if _is_gz(out_path) else "w"
    with _open_text(out_path, mode_header) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

    manager = mp.Manager()
    lock = manager.Lock()

    if workers is None or workers <= 0:
        workers = mp.cpu_count()

    errors: dict[str, list[str]] = {}
    diagrams = list(diagrams)  # so we know len for tqdm

    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=_init_worker,
        initargs=(lock, str(out_path), fieldnames, invariants),
    ) as ex:
        future_to_k: dict = {}
        for k in diagrams:
            k_name = getattr(k, "name", str(k))
            future_to_k[ex.submit(_compute_and_write_row, k)] = (k_name, k)

        # Show progress while consuming completed futures
        for fut in tqdm(as_completed(future_to_k), total=len(diagrams), desc="Computing invariants"):
            k_name, k_obj = future_to_k[fut]
            try:
                name, err_list = fut.result()
            except Exception as e:
                # Worker crashed before it could write: record an error and still write a row with Nones
                errors.setdefault(k_name, []).append(f"worker crashed: {e!r}")
                mode_append = "at" if _is_gz(out_path) else "a"
                with lock:
                    with _open_text(out_path, mode_append) as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        try:
                            diag_str = to_knotpy_notation(k_obj)
                        except Exception:
                            diag_str = str(k_obj)
                        row = {"name": k_name, "knotpy notation": diag_str}
                        for inv in invariants:
                            row[inv] = None
                        writer.writerow(row)
                continue

            if err_list:
                errors[name] = err_list
            else:
                errors.setdefault(name, [])

    return errors