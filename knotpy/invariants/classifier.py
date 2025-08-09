# knotpy/tables/classifier.py
from __future__ import annotations

import os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import defaultdict
from typing import Callable, Iterable, Mapping, Any

from tqdm import tqdm
from knotpy.tables.invariant_writer import save_invariant_table


# --- Helpers (single-invariant) ------------------------------------------------
def _compute_key_single(args: tuple[Any, Callable[[Any], Any]]) -> tuple[Any | None, Any]:
    """Compute single invariant; return (key, diagram) or (None, diagram) on error."""
    k, func = args
    try:
        return func(k), k
    except Exception:
        return None, k


def _save_key_single(args: tuple[Any, Callable[[Any], Any], Path]) -> None:
    """Compute single invariant and save to a per-diagram file in a directory."""
    k, func, path = args
    try:
        value = func(k)
        filename = path / f"{k.name}.json" if hasattr(k, "name") else path / "unnamed.json"
        save_invariant_table(filename=filename, table=[{"diagram": k, "value": value}])
    except Exception:
        return


# --- Helpers (multi-invariant) -------------------------------------------------
def _compute_key_multi(
    args: tuple[Any, Mapping[str, Callable[[Any], Any]]]
) -> tuple[tuple[tuple[str, Any], ...] | None, Any]:
    """Compute multiple invariants; return (key-tuple, diagram) or (None, diagram) on error."""
    k, invariant_funcs = args
    try:
        key = tuple((name, func(k)) for name, func in invariant_funcs.items())
        return key, k
    except Exception:
        return None, k


def _save_key_multi(args: tuple[Any, Mapping[str, Callable[[Any], Any]], Path]) -> None:
    """Compute multiple invariants and save to a per-diagram file in a directory."""
    k, invariant_funcs, path = args
    try:
        key = tuple((name, func(k)) for name, func in invariant_funcs.items())
        filename = path / f"{k.name}.json" if hasattr(k, "name") else path / "unnamed.json"
        save_invariant_table(filename=filename, table=[{"diagram": k} | dict(key)])
    except Exception:
        return


# --- Public API ----------------------------------------------------------------
def group_by_invariants(
    diagrams: Iterable[Any],
    invariant_funcs: Mapping[str, Callable[[Any], Any]] | Callable[[Any], Any],
    parallel: bool = True,
    max_workers: int | None = None,
) -> dict[Any, list[Any]]:
    """Group diagrams by shared invariant values.

    Args:
        diagrams: Iterable of diagram-like objects.
        invariant_funcs:
            - If a mapping ``{name: func}``, group by multiple invariants.
              The key is a tuple ``((name, value), ...)`` (order follows ``dict.items()``).
            - If a single callable, group by that invariant value.
        parallel: Compute invariants in parallel using processes.
        max_workers: Number of workers; defaults to ``os.cpu_count()``.

    Returns:
        Mapping from invariant key(s) to a list of diagrams.

    Notes:
        - Functions must be picklable for process pools (no lambdas/closures).
        - Exceptions in worker functions are swallowed; the offending diagram is skipped.
    """
    grouped: dict[Any, list[Any]] = defaultdict(list)
    is_single = callable(invariant_funcs)

    if parallel:
        with ProcessPoolExecutor(max_workers=max_workers or os.cpu_count()) as executor:
            args = [(d, invariant_funcs) for d in diagrams]
            submit_fn = _compute_key_single if is_single else _compute_key_multi
            futures = [executor.submit(submit_fn, arg) for arg in args]

            with tqdm(total=len(futures), desc="Computing invariants", unit="item") as pbar:
                for future in as_completed(futures):
                    key, diagram = future.result()
                    if key is not None:
                        grouped[key].append(diagram)
                    pbar.update(1)
    else:
        for diagram in tqdm(list(diagrams), desc="Computing invariants", unit="item"):
            try:
                if is_single:
                    key = invariant_funcs(diagram)  # type: ignore[misc]
                else:
                    key = tuple(
                        (name, func(diagram))  # type: ignore[union-attr]
                        for name, func in invariant_funcs.items()  # type: ignore[union-attr]
                    )
                grouped[key].append(diagram)
            except Exception:
                pass  # optionally log

    return dict(grouped)


def save_invariants(
    diagrams: Iterable[Any],
    invariant_funcs: Mapping[str, Callable[[Any], Any]] | Callable[[Any], Any],
    path: str | Path,
    parallel: bool = True,
    max_workers: int | None = None,
) -> None:
    """Compute and save invariants for diagrams.

    Two modes:
        - **parallel=True**: treat ``path`` as a **directory** and write **one file per diagram**.
        - **parallel=False**: treat ``path`` as a **single file** and write a **combined table**.

    Args:
        diagrams: Iterable of diagram-like objects.
        invariant_funcs:
            - Mapping ``{name: func}`` for multi-invariant output.
            - Single callable for single-invariant output.
        path: Directory (parallel) or file path (sequential).
        parallel: Use process pool and per-diagram files when True.
        max_workers: Number of workers; defaults to ``os.cpu_count()``.

    Raises:
        ValueError: If ``parallel`` is True and ``path`` is not a directory.
        ValueError: If ``parallel`` is False and ``path`` already exists as a directory.
    """
    is_single = callable(invariant_funcs)
    save_path = Path(path)

    if parallel:
        if not save_path.is_dir():
            raise ValueError("For parallel=True, 'path' must be an existing directory.")
        with ProcessPoolExecutor(max_workers=max_workers or os.cpu_count()) as executor:
            args = [(d, invariant_funcs, save_path) for d in diagrams]
            submit_fn = _save_key_single if is_single else _save_key_multi
            futures = [executor.submit(submit_fn, arg) for arg in args]
            with tqdm(total=len(futures), desc="Computing invariants", unit="item") as pbar:
                for _ in as_completed(futures):
                    pbar.update(1)
    else:
        if save_path.is_dir():
            raise ValueError("For parallel=False, 'path' must be a file (not a directory).")

        table: list[dict[str, Any]] = []
        for diagram in tqdm(list(diagrams), desc="Computing invariants", unit="item"):
            try:
                if is_single:
                    value = invariant_funcs(diagram)  # type: ignore[misc]
                    table.append({"diagram": diagram, "value": value})
                else:
                    key = tuple(
                        (name, func(diagram))  # type: ignore[union-attr]
                        for name, func in invariant_funcs.items()  # type: ignore[union-attr]
                    )
                    table.append({"diagram": diagram} | dict(key))
            except Exception:
                pass  # optionally log

        save_invariant_table(filename=save_path, table=table)
