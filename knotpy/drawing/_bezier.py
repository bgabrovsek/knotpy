# knotpy/drawing/_bezier.py

"""
Lightweight Bézier helpers used by the drawing subsystem.

This module intentionally avoids importing heavyweight libraries at import time.
In particular, `matplotlib` is **only imported inside functions** that need it,
so that `import knotpy` remains fast even if drawing is not used.

Functions
---------
- _bezier_function(z0, z1, z2, derivative=0)
    Return a callable for a quadratic Bézier curve (or its 1st/2nd derivative).
- bezier(*z, straight_lines=False)
    Create a matplotlib Path for a polyline (degree 1) or quadratic Bézier (degree 2).
"""

from __future__ import annotations

from typing import Callable


__all__ = ["_bezier_function", "bezier"]


def _bezier_function(
    z0: complex,
    z1: complex,
    z2: complex,
    derivative: int = 0,
) -> Callable[[float], complex]:
    """
    Return Bézier curve through control points z0, z1, z2. The curve is as the function or its derivative.

    Args:
        z0: Control point.
        z1: Control point.
        z2: Control point.
        derivative: Order of derivative to return (0 = curve, 1 = first derivative, 2 = second derivative).

    Return:
        Callable[[float], complex]: A function f(t) with t in [0, 1] returning the complex plane point (or derivative).

    Notes:
        - This is a *quadratic* Bézier (degree 2). For derivative=0 the formula is:
              B(t) = (1 - t) * ((1 - t) * z0 + t * z1) + t * ((1 - t) * z1 + t * z2)
        - For derivative=1 and derivative=2, the standard analytic derivatives are returned.
        - Higher derivatives are not implemented for quadratic curves.

    Raises:
        NotImplementedError: If `derivative` is not 0, 1, or 2.
    """
    if derivative == 0:
        return lambda t: (1 - t) * ((1 - t) * z0 + t * z1) + t * ((1 - t) * z1 + t * z2)
    if derivative == 1:
        return lambda t: 2 * (1 - t) * (z1 - z0) + 2 * t * (z2 - z1)
    if derivative == 2:
        return lambda t: 2 * (z2 - 2 * z1 + z0)
    raise NotImplementedError("derivatives higher than 2 not implemented")


def bezier(*z: complex, straight_lines: bool = False):
    """
    Draw a Bézier curve of degree 1 or 2.

    Args:
        *z: List of coordinates as complex numbers. For quadratic Bézier segments,
            supply three points (z0, z1, z2). For straight polylines, supply 2+ points.
        straight_lines: Bézier curve degree (False = quadratic, True = degree-1 straight segments).

    Return:
        matplotlib.path.Path: A Path describing the requested curve(s).

    Notes:
        - Import of matplotlib is **local** to keep module import cheap.
        - `straight_lines=True` uses Path.LINETO between successive points.
        - `straight_lines=False` uses Path.CURVE3 (quadratic) codes; each additional point
          after the first is treated as part of a quadratic segment consistent with your
          original usage.

    Example:
        >>> from math import pi
        >>> p = bezier(0+0j, 1+1j, 2+0j)           # quadratic path
        >>> q = bezier(0+0j, 1+1j, 2+0j, straight_lines=True)  # polyline
    """
    # Local import to avoid slowing down package import when drawing is unused.
    from matplotlib.path import Path  # type: ignore

    if len(z) < 2:
        raise ValueError("bezier() requires at least two points")

    vertices = [(w.real, w.imag) for w in z]
    # MOVETO for the first point; LINETO for straight lines else CURVE3 for quadratic segments.
    codes = [Path.MOVETO] + [Path.LINETO if straight_lines else Path.CURVE3] * (len(z) - 1)
    return Path(vertices, codes)