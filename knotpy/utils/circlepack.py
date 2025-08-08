"""
Implements a fast, dependency-free algorithm for packing circles with
prescribed tangencies. Used internally in KnotPy for layout of graph structures.
"""

__all__ = [
    "circle_pack",
    "invert_packing",
    "normalize_packing",
    "invert_around",
]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

tolerance = 1 + 1e-12  # Convergence threshold


def circle_pack(internal: dict[str, list[str]], external: dict[str, float]) -> dict[str, tuple[complex, float]]:
    """
    Compute a circle packing layout given prescribed tangencies.

    Internal circles are surrounded by a cycle of other circles; external circles
    have fixed radii.

    Args:
        internal: Mapping of internal keys to cyclic list of neighbor keys.
        external: Mapping of external keys to fixed radii.

    Returns:
        A dictionary mapping each key to a (center, radius) pair.

    Raises:
        ValueError: If keys are not disjoint or external radii are non-positive.

    Example:
        >>> internal = {'A': ['B', 'C', 'D']}
        >>> external = {'B': 1.0, 'C': 1.0, 'D': 1.0}
        >>> packing = circle_pack(internal, external)
        >>> len(packing)
        4
    """
    from math import pi, sin

    if min(external.values()) <= 0:
        raise ValueError("circle_pack: external radii must be positive")
    radii = dict(external)

    for k in internal:
        if k in external:
            raise ValueError("circle_pack: keys are not disjoint")
        radii[k] = 1.0  # Initial guess

    last_change = 2.0
    while last_change > tolerance:
        last_change = 1.0
        for k in internal:
            theta = flower(radii, k, internal[k])
            n = len(internal[k])
            # Estimate new radius based on current angle sum
            hat = radii[k] / (1 / sin(theta / (2 * n)) - 1)
            new_rad = hat * (1 / (sin(pi / n)) - 1)
            ratio = max(new_rad / radii[k], radii[k] / new_rad)
            last_change = max(last_change, ratio)
            radii[k] = new_rad

    placements: dict[str, complex] = {}
    k1 = next(iter(internal))
    k2 = internal[k1][0]
    placements[k1] = 0j
    placements[k2] = radii[k1] + radii[k2]
    place(placements, radii, internal, k1)
    place(placements, radii, internal, k2)

    return {k: (placements[k], radii[k]) for k in radii}


def invert_packing(packing: dict[str, tuple[complex, float]], center: complex) -> dict[str, tuple[complex, float]]:
    """
    Invert all circles in the packing around a given complex point.

    Args:
        packing: Dictionary mapping keys to (center, radius) pairs.
        center: Complex point to invert around.

    Returns:
        A new packing where all circles are inverted.

    Example:
        >>> inverted = invert_packing(packing, 0j)
    """
    result: dict[str, tuple[complex, float]] = {}
    for k, (z, r) in packing.items():
        z -= center
        offset = z / abs(z) if z != 0 else 1j
        p, q = z - offset * r, z + offset * r
        p, q = 1 / p, 1 / q
        z_new = (p + q) / 2
        r_new = abs((p - q) / 2)
        result[k] = (z_new, r_new)
    return result


def normalize_packing(packing: dict[str, tuple[complex, float]], k: str = None, target: float = 1.0) -> dict[str, tuple[complex, float]]:
    """
    Normalize the packing so that a given circle has radius `target`.

    Args:
        packing: Mapping from keys to (center, radius).
        k: Optional key of the circle to normalize. If None, uses the smallest.
        target: Desired radius for the selected circle.

    Returns:
        New packing with all circles scaled accordingly.
    """
    if k is None:
        r = min(r for _, r in packing.values())
    else:
        _, r = packing[k]
    s = target / r
    return {kk: (zz * s, rr * s) for kk, (zz, rr) in packing.items()}


def invert_around(packing: dict[str, tuple[complex, float]], k: str, smallCircles: list[str] | None = None) -> dict[str, tuple[complex, float]]:
    """
    Invert packing so that circle `k` surrounds the others.

    This finds a Möbius transform (via inversion) that places circle `k` large
    enough to contain the others, based on a grid search.

    Args:
        packing: The circle packing to invert.
        k: Key of the desired outer circle.
        smallCircles: Optional list of keys to consider in optimization.

    Returns:
        A new packing with optimized inversion.
    """
    z, r = packing[k]
    optpack = {kk: packing[kk] for kk in smallCircles} if smallCircles else packing
    q, g = z, r * 0.4
    old_rad = None
    ratio = 2.0

    while abs(g) > r * (tolerance - 1) or ratio > tolerance:
        rr, _, _, q = max(test_grid(optpack, k, z, r, q, g))
        if old_rad:
            ratio = rr / old_rad
        old_rad = rr
        g *= 0.53 + 0.1j  # rotate grid step

    return invert_packing(packing, q)

# Internal utilities

def acxyz(x: float, y: float, z: float) -> float:
    """Angle at x between y and z using circle geometry."""
    from math import acos, pi
    try:
        return acos(((x + y) ** 2 + (x + z) ** 2 - (y + z) ** 2) / (2.0 * (x + y) * (x + z)))
    except (ValueError, ZeroDivisionError):
        return pi / 3 if x else pi


def flower(radius: dict[str, float], center: str, cycle: list[str]) -> float:
    """Sum of angles at center formed with its neighboring cycle."""
    return sum(acxyz(radius[center], radius[cycle[i - 1]], radius[cycle[i]])
               for i in range(len(cycle)))


def place(placements: dict[str, complex], radii: dict[str, float], internal: dict[str, list[str]], center: str) -> None:
    """Recursively place neighbors of a given center based on geometry."""
    from math import e
    if center not in internal:
        return
    cycle = internal[center]
    for i in range(-len(cycle), len(cycle) - 1):
        if cycle[i] in placements and cycle[i + 1] not in placements:
            s, t = cycle[i], cycle[i + 1]
            theta = acxyz(radii[center], radii[s], radii[t])
            offset = (placements[s] - placements[center]) / (radii[s] + radii[center])
            offset *= e ** (-1j * theta)
            placements[t] = placements[center] + offset * (radii[t] + radii[center])
            place(placements, radii, internal, t)


def test_grid(packing: dict[str, tuple[complex, float]], k: str, z: complex, r: float, q: complex, g: complex):
    """Yield candidate centers and their resulting smallest radius after inversion and normalization."""
    for i in (-2, -1, 0, 1, 2):
        for j in (-2, -1, 0, 1, 2):
            center = q + i * g + j * 1j * g
            if abs(center - z) < r:
                newpack = invert_packing(packing, center)
                newpack = normalize_packing(newpack, k)
                minrad = min(rr for _, rr in newpack.values())
                yield minrad, i, j, center