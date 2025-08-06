import os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from collections import defaultdict
from tqdm import tqdm
from knotpy.tables.invariant_writer import save_invariant_table

# --- Helper for single-invariant case ---
def _compute_key_single(args):
    k, func = args
    try:
        return func(k), k
    except Exception:
        return None, k

# --- Helper for single-invariant case ---
def _save_key_single(args):
    k, func, path = args
    try:
        value = func(k)
        filename = path / str(k.name)
        save_invariant_table(filename=path, table=[{"diagram": k, "value": value}])
        return
    except Exception:
        return

# --- Helper for multi-invariant case ---
def _compute_key_multi(args):
    k, invariant_funcs = args
    try:
        key = tuple((name, func(k)) for name, func in invariant_funcs.items())
        return key, k
    except Exception:
        return None, k

# --- Helper for multi-invariant case ---
def _save_key_multi(args):
    k, invariant_funcs, path = args
    try:
        key = tuple((name, func(k)) for name, func in invariant_funcs.items())
        filename = path / str(k.name)
        save_invariant_table(filename=path, table=[{"diagram": k} | dict(key)])
        return
    except Exception:
        return

# --- Main grouping function ---
def group_by_invariants(diagrams, invariant_funcs, parallel=True, max_workers=None):
    """
    Group diagrams by shared invariant values.

    Parameters:
        diagrams (list): List of diagram-like objects (e.g., knotoids, links).
        invariant_funcs (dict or callable): Either:
            - A dict {name: function}, to group by multiple invariants (key = tuple of (name, value))
            - A single function, to group by a single invariant (key = value)
        parallel (bool): Whether to compute invariants in parallel.
        max_workers (int or None): Number of parallel workers (default: all CPUs).

    Returns:
        dict: Mapping of invariant key(s) to list of diagrams.
    """
    grouped = defaultdict(list)
    is_single = callable(invariant_funcs)

    if parallel:
        with ProcessPoolExecutor(max_workers=max_workers or os.cpu_count()) as executor:
            if is_single:
                args = [(d, invariant_funcs) for d in diagrams]
                futures = [executor.submit(_compute_key_single, arg) for arg in args]
            else:
                args = [(d, invariant_funcs) for d in diagrams]
                futures = [executor.submit(_compute_key_multi, arg) for arg in args]

            with tqdm(total=len(futures), desc="Computing invariants", unit="item") as pbar:
                for future in as_completed(futures):
                    key, diagram = future.result()
                    if key is not None:
                        grouped[key].append(diagram)
                    pbar.update(1)
    else:
        for diagram in tqdm(diagrams, desc="Computing invariants", unit="item"):
            try:
                if is_single:
                    key = invariant_funcs(diagram)
                else:
                    key = tuple((name, func(diagram)) for name, func in invariant_funcs.items())
                grouped[key].append(diagram)
            except Exception:
                pass  # optionally log

    return dict(grouped)


# --- Main grouping function ---
def save_invariants(diagrams, invariant_funcs, path, parallel=True, max_workers=None):
    """
    Group diagrams by shared invariant values.

    Parameters:
        diagrams (list): List of diagram-like objects (e.g., knotoids, links).
        invariant_funcs (dict or callable): Either:
            - A dict {name: function}, to group by multiple invariants (key = tuple of (name, value))
            - A single function, to group by a single invariant (key = value)
        parallel (bool): Whether to compute invariants in parallel.
        max_workers (int or None): Number of parallel workers (default: all CPUs).

    Returns:
        dict: Mapping of invariant key(s) to list of diagrams.
    """
    is_single = callable(invariant_funcs)
    save_path = Path(path)


    if parallel:

        if not save_path.is_dir():
            raise ValueError("The specified path is not a directory.")

        with ProcessPoolExecutor(max_workers=max_workers or os.cpu_count()) as executor:
            args = [(d, invariant_funcs) for d in diagrams]
            func = _compute_key_single if is_single else _compute_key_multi

            futures = [executor.submit(func, arg) for arg in args]

            with tqdm(total=len(futures), desc="Computing invariants", unit="item") as pbar:
                for _ in as_completed(futures):
                    pbar.update(1)

    else:

        if save_path.is_dir():
            raise ValueError("The specified path is an existingdirectory (should be a file).")


        table = list()

        for diagram in tqdm(diagrams, desc="Computing invariants", unit="item"):
            try:
                if is_single:
                    key = invariant_funcs(diagram)
                    table.append({"diagram": diagram, "value": key})
                else:
                    key = tuple((name, func(diagram)) for name, func in invariant_funcs.items())
                    table.append({"diagram": diagram} | dict(key))
            except Exception:
                pass  # optionally log

        save_invariant_table(filename=save_path, table=table)