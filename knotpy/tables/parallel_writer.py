from __future__ import annotations

import csv
import gzip
import io
import os
import re
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Callable, Iterable

from tqdm import tqdm
from knotpy.notation.native import to_knotpy_notation

# --- Globals initialized in each worker process --------------------------------

_OUT_DIR: str | None = None
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
        if "b" in mode:
            mode = mode.replace("b", "")
        if "t" not in mode:
            mode = mode + "t"
        return gzip.open(path, mode=mode, encoding="utf-8", newline="")
    mode = mode.replace("t", "")
    return open(path, mode=mode, encoding="utf-8", newline="")



def _init_worker(out_dir: str, fieldnames: list[str], invariants: dict[str, Callable]) -> None:
    global _OUT_DIR, _FIELDNAMES, _INVARIANTS
    _OUT_DIR = out_dir
    _FIELDNAMES = fieldnames
    _INVARIANTS = invariants

_SAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]+")

def _safe_slug(s: str, max_len: int = 80) -> str:
    s = s.strip().replace(" ", "_")
    s = _SAFE_CHARS.sub("_", s)
    return s[:max_len] if len(s) > max_len else s

def _row_path(idx: int, name: str) -> Path:
    print("od", _OUT_DIR)
    assert _OUT_DIR is not None
    # include idx first so merge is easy and stable; name is just for readability
    slug = _safe_slug(name)
    return Path(_OUT_DIR) / "rows" / f"{idx:08d}__{slug}.csvl"



def _err_path(idx: int, name: str) -> Path:
    assert _OUT_DIR is not None
    slug = _safe_slug(name)
    return Path(_OUT_DIR) / "errors" / f"{idx:08d}__{slug}.err.txt"


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)

def _compute_and_write_single(idx: int, diagram) -> None:
    """
    Worker task:
      - if result already exists and is non-empty: SKIP
      - otherwise compute row
      - write one CSV line into its own file (atomic)
      - write error file if needed (atomic)
    """
    assert _FIELDNAMES is not None and _INVARIANTS is not None

    name = getattr(diagram, "name", str(diagram))
    row_path = _row_path(idx, name)

    # ---- NEW: skip if already computed --------------------------------------
    if row_path.exists() and row_path.stat().st_size > 0:
        return
    # -------------------------------------------------------------------------

    err_msgs: list[str] = []

    # Serialize diagram (best-effort)
    try:
        diag_str = to_knotpy_notation(diagram)
    except Exception as e:
        diag_str = str(diagram)
        err_msgs.append(f"to_knotpy_notation failed: {e!r}")

    # Compute invariants
    values: dict[str, object] = {}
    for inv_name, inv_fn in _INVARIANTS.items():
        try:
            values[inv_name] = inv_fn(diagram)
        except Exception as e:
            values[inv_name] = None
            err_msgs.append(f"{inv_name} failed: {e!r}")

    # Build row
    row = {"name": name, "knotpy notation": diag_str}
    row.update(values)

    # Convert to exactly one CSV line (no header)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=_FIELDNAMES, extrasaction="ignore")
    writer.writerow(row)
    line = buf.getvalue()

    # Atomic write of row
    _atomic_write_text(row_path, line)

    # Atomic write of errors (if any)
    if err_msgs:
        err_path = _err_path(idx, name)
        _atomic_write_text(err_path, "\n".join(err_msgs) + "\n")



#
# def _compute_and_write_row(diagram) -> tuple[str, list[str]]:
#     """
#     Compute invariant values for a single diagram and append a CSV row.
#
#     Returns:
#         (name, error_messages)
#     """
#     assert _LOCK is not None and _FILENAME and _FIELDNAMES and _INVARIANTS is not None
#
#     name = getattr(diagram, "name", str(diagram))
#     err_msgs: list[str] = []
#
#     # Serialize diagram (best-effort)
#     try:
#         diag_str = to_knotpy_notation(diagram)
#     except Exception as e:
#         diag_str = str(diagram)
#         err_msgs.append(f"to_knotpy_notation failed for {name}: {e!r}")
#
#     # Compute invariants
#     values: dict[str, object] = {}
#     for inv_name, inv_fn in _INVARIANTS.items():
#         try:
#             values[inv_name] = inv_fn(diagram)
#         except Exception as e:
#             values[inv_name] = None
#             err_msgs.append(f"{inv_name} failed for {name}: {e!r}")
#
#     # Append a CSV row (guarded by a lock so writes don’t interleave)
#     row = {"name": name, "diagram": diag_str}
#     row.update(values)
#
#     print("\n[[", row, "]]\n", flush=True)
#
#     with open("parallel_results.txt", "a", encoding="utf-8") as f:
#         f.write(str(row) + "\n")
#
#     with _LOCK:
#         mode = "at" if _is_gz(_FILENAME) else "a"
#         with _open_text(_FILENAME, mode) as f:
#             writer = csv.DictWriter(f, fieldnames=_FIELDNAMES)
#             writer.writerow(row)
#
#     return name, err_msgs


def save_invariants_parallel(
    filename: str | Path,
    diagrams: Iterable,
    invariants: dict[str, Callable],
    workers: int = 0,
    scratch_dir: str | Path | None = None,
) -> dict[str, list[str]]:
    """
    Two-phase parallel writer:

    Phase 1:
      - parallel compute, each result written as ONE CSV row line in its own file under scratch_dir
    Phase 2:
      - verify all row files exist
      - merge them into final CSV (or .csv.gz) with a single header

    Returns:
      dict[name -> list[str]] of error messages collected from per-diagram error files.
      (Row values are NOT collected in memory.)
    """
    out_path = Path(filename)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Where per-task row/error files go
    if scratch_dir is None:
        scratch_dir = out_path.parent / (out_path.stem + "__parts")
    scratch_dir = Path(scratch_dir)
    (scratch_dir / "rows").mkdir(parents=True, exist_ok=True)
    (scratch_dir / "errors").mkdir(parents=True, exist_ok=True)

    fieldnames = ["name", "knotpy notation"] + list(invariants.keys())

    # Materialize diagrams so we know N and preserve stable input order for merging
    diagrams = list(diagrams)
    n = len(diagrams)

    print(str(scratch_dir), fieldnames, invariants)

    if workers is None or workers <= 0:
        workers = os.cpu_count() or 1

    # --- Phase 1: parallel compute -> per-task files ---------------------------
    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=_init_worker,
        initargs=(str(scratch_dir), fieldnames, invariants),
    ) as ex:
        futures = [ex.submit(_compute_and_write_single, i, d) for i, d in enumerate(diagrams)]

        for fut in tqdm(as_completed(futures), total=n, desc="Computing invariants"):
            # IMPORTANT: don't collect row results; just ensure exceptions surface
            fut.result()

    # --- Phase 2: verify + merge ------------------------------------------------
    # set global vars
    global _OUT_DIR
    _OUT_DIR = str(scratch_dir)

    missing: list[tuple[int, str, Path]] = []
    row_files: list[Path] = []

    for i, d in enumerate(diagrams):
        print(i, d)
        name = d.name
        #name = getattr(d.attr, "name", str(d))
        print("name", name)
        rp = _row_path(i, name)
        if not rp.exists() or rp.stat().st_size == 0:
            missing.append((i, name, rp))
        else:
            row_files.append(rp)

    if missing:
        # Raise with a helpful message; caller can catch and inspect.
        msg_lines = ["Missing or empty per-diagram result files:"]
        for i, name, rp in missing[:50]:
            msg_lines.append(f"  idx={i} name={name!r} path={str(rp)}")
        if len(missing) > 50:
            msg_lines.append(f"  ... and {len(missing) - 50} more")
        raise RuntimeError("\n".join(msg_lines))

    # Write final output (fresh) + header, then append row lines in order
    mode_header = "wt" if _is_gz(out_path) else "w"
    with _open_text(out_path, mode_header) as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        # append lines (already CSV-encoded) in original order
        for i, d in enumerate(diagrams):
            name = getattr(d, "name", str(d))
            rp = _row_path(i, name)
            with open(rp, "r", encoding="utf-8", newline="") as f_in:
                line = f_in.read()
                # ensure exactly one row line ends with newline
                if line and not line.endswith("\n"):
                    line += "\n"
                f_out.write(line)

    # Collect errors from error files (small; ok to collect)
    errors: dict[str, list[str]] = {}
    for i, d in enumerate(diagrams):
        name = getattr(d, "name", str(d))
        ep = _err_path(i, name)
        if ep.exists() and ep.stat().st_size > 0:
            errors[name] = ep.read_text(encoding="utf-8").splitlines()
        else:
            errors.setdefault(name, [])

    return errors
#
#
# def save_invariants_parallel(
#     filename: str | Path,
#     diagrams: Iterable,
#     invariants: dict[str, Callable],
#     workers: int = 0,
# ) -> dict[str, list[str]]:
#     """
#     Compute invariants for many diagrams in parallel and save to CSV (or ``.csv.gz``).
#
#     The output file will contain a header with ``name``, ``diagram``, and one column
#     per invariant key in ``invariants``.
#
#     Args:
#         filename: Output CSV path (created if missing). Parent dirs will be created.
#                   If the name ends with ``.gz``, a gzipped CSV is written.
#         diagrams: Iterable of diagram objects. Each should have a ``.name`` or be
#                   convertible to ``str(diagram)``.
#         invariants: Mapping ``{column_name: callable(diagram) -> value}``.
#         workers: Number of worker processes. ``<= 0`` means use ``mp.cpu_count()``.
#
#     Returns:
#         dict mapping diagram name -> list of error messages (empty list if none).
#     """
#     out_path = Path(filename)
#     out_path.parent.mkdir(parents=True, exist_ok=True)
#
#     fieldnames = ["name", "knotpy notation"] + list(invariants.keys())
#
#     # Create/overwrite file and write header
#     mode_header = "wt" if _is_gz(out_path) else "w"
#     with _open_text(out_path, mode_header) as f:
#         writer = csv.DictWriter(f, fieldnames=fieldnames)
#         writer.writeheader()
#
#     manager = mp.Manager()
#     lock = manager.Lock()
#
#     if workers is None or workers <= 0:
#         workers = mp.cpu_count()
#
#     errors: dict[str, list[str]] = {}
#     diagrams = list(diagrams)  # so we know len for tqdm
#
#     with ProcessPoolExecutor(
#         max_workers=workers,
#         initializer=_init_worker,
#         initargs=(lock, str(out_path), fieldnames, invariants),
#     ) as ex:
#         future_to_k: dict = {}
#         for k in diagrams:
#             k_name = getattr(k, "name", str(k))
#             future_to_k[ex.submit(_compute_and_write_row, k)] = (k_name, k)
#
#         # Show progress while consuming completed futures
#         for fut in tqdm(as_completed(future_to_k), total=len(diagrams), desc="Computing invariants"):
#             k_name, k_obj = future_to_k[fut]
#             try:
#                 name, err_list = fut.result()
#             except Exception as e:
#                 # Worker crashed before it could write: record an error and still write a row with Nones
#                 errors.setdefault(k_name, []).append(f"worker crashed: {e!r}")
#                 mode_append = "at" if _is_gz(out_path) else "a"
#                 with lock:
#                     with _open_text(out_path, mode_append) as f:
#                         writer = csv.DictWriter(f, fieldnames=fieldnames)
#                         try:
#                             diag_str = to_knotpy_notation(k_obj)
#                         except Exception:
#                             diag_str = str(k_obj)
#                         row = {"name": k_name, "knotpy notation": diag_str}
#                         for inv in invariants:
#                             row[inv] = None
#                         writer.writerow(row)
#                 continue
#
#             if err_list:
#                 errors[name] = err_list
#             else:
#                 errors.setdefault(name, [])
#
#     return errors