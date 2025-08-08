from __future__ import annotations

import csv
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Tuple, Union, Optional

import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed

from tqdm import tqdm
from knotpy.notation.native import to_knotpy_notation

# Globals for worker processes
_LOCK: Optional[mp.synchronize.Lock] = None
_FILENAME: Optional[str] = None
_FIELDNAMES: Optional[List[str]] = None
_INVARIANTS: Optional[Dict[str, Callable]] = None


def _init_worker(lock: mp.synchronize.Lock,
                 filename: str,
                 fieldnames: List[str],
                 invariants: Dict[str, Callable]) -> None:
    global _LOCK, _FILENAME, _FIELDNAMES, _INVARIANTS
    _LOCK = lock
    _FILENAME = filename
    _FIELDNAMES = fieldnames
    _INVARIANTS = invariants


def _compute_and_write_row(diagram) -> Tuple[str, List[str]]:
    assert _LOCK is not None and _FILENAME and _FIELDNAMES and _INVARIANTS is not None

    name = getattr(diagram, "name", str(diagram))
    err_msgs = []

    try:
        diag_str = to_knotpy_notation(diagram)
    except Exception as e:
        diag_str = str(diagram)
        err_msgs.append(f"to_knotpy_notation failed for {name}: {e!r}")

    values: Dict[str, object] = {}
    for inv_name, inv_fn in _INVARIANTS.items():
        try:
            values[inv_name] = inv_fn(diagram)
        except Exception as e:
            values[inv_name] = None
            err_msgs.append(f"{inv_name} failed for {name}: {e!r}")

    row = {"name": name, "diagram": diag_str}
    row.update(values)

    with _LOCK:
        with open(_FILENAME, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=_FIELDNAMES)
            writer.writerow(row)

    return name, err_msgs


def save_invariants_parallel(
    filename: Union[str, Path],
    diagrams: Iterable,
    invariants: Dict[str, Callable],
    workers: int = 0,
) -> Dict[str, List[str]]:
    """
    Same as before, but with tqdm progress tracking.
    """
    out_path = Path(filename)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["name", "diagram"] + list(invariants.keys())

    # Empty file + header
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

    manager = mp.Manager()
    lock = manager.Lock()

    if workers is None or workers <= 0:
        workers = mp.cpu_count()

    errors: Dict[str, List[str]] = {}
    diagrams = list(diagrams)  # so we know len for tqdm

    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=_init_worker,
        initargs=(lock, str(out_path), fieldnames, invariants),
    ) as ex:
        future_to_k = {}
        for k in diagrams:
            k_name = getattr(k, "name", str(k))
            future_to_k[ex.submit(_compute_and_write_row, k)] = (k_name, k)

        # Wrap as_completed with tqdm
        for fut in tqdm(as_completed(future_to_k), total=len(diagrams), desc="Computing invariants"):
            k_name, k_obj = future_to_k[fut]
            try:
                name, err_list = fut.result()
            except Exception as e:
                errors.setdefault(k_name, []).append(f"worker crashed: {e!r}")
                with lock:
                    with open(out_path, "a", newline="", encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        try:
                            diag_str = to_knotpy_notation(k_obj)
                        except Exception:
                            diag_str = str(k_obj)
                        row = {"name": k_name, "diagram": diag_str}
                        for inv in invariants:
                            row[inv] = None
                        writer.writerow(row)
                continue

            if err_list:
                errors[name] = err_list
            else:
                errors.setdefault(name, {})

    return errors
