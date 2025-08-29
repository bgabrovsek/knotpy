"""
Geometric alignment utilities for diagram layouts.

This module provides helpers to:
- Rotate a set of circles to a canonical orientation using PCA on their centers.
- Place multiple (layout, circles) pairs side by side with a consistent gap.

Heavy dependencies (e.g., scikit-learn) are imported **locally** inside the
functions that need them, so importing `knotpy.drawing` remains fast.
"""

from __future__ import annotations

import math
from statistics import mean

from knotpy.utils.geometry import Circle, bounding_box, translate

__all__ = ["canonically_rotate_circles", "align_layouts"]
__version__ = "0.2"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"


def _principal_component_analysis(complex_points: list[complex], angle: float = 0.0) -> list[complex]:
    """Rotate points to align with the first principal component (plus an extra rotation).

    The input is a list of complex numbers (x + iy). We compute PCA on the
    coordinate pairs, align the points with the first principal component, and
    then rotate by ``angle`` (in radians).

    Args:
        complex_points: Points to rotate, given as complex numbers (x + iy).
        angle: Additional rotation (in radians) applied after aligning with the
            first principal component.

    Return:
        list[complex]: Rotated points as complex numbers.

    Notes:
        - scikit-learn (PCA) is imported locally to avoid slowing module import.
        - The first PC is normalized and used to build the rotation.
    """
    # Local import to keep top-level import time small.
    from sklearn.decomposition import PCA  # type: ignore

    # Convert complex numbers to a 2D array
    points_2d = [[z.real, z.imag] for z in complex_points]

    # Fit PCA model to the data
    pca = PCA(n_components=2)
    pca.fit(points_2d)

    # Extract the principal components and normalize; use conjugate to map to complex plane
    conjugated_principal_components = [complex(c[0], -c[1]) for c in pca.components_]
    conjugated_principal_components = [c / abs(c) for c in conjugated_principal_components]  # normalize

    # Align along the first principal component, then rotate by 'angle'
    conj_princ_comp = conjugated_principal_components[0] * complex(math.cos(angle), math.sin(angle))
    return [z * conj_princ_comp for z in complex_points]


def canonically_rotate_circles(circles: dict, degree: int = 0) -> dict:
    """Rotate a system of circles to a canonical orientation via PCA.

    Given a mapping where values are :class:`Circle` instances, compute the
    PCA of their centers (weighted by radius for the mass center), translate to
    the center of mass, align with the first principal component, optionally
    rotate by ``degree`` (degrees), and (if needed) flip so more mass lies to
    the right (positive real axis).

    If ``degree = 0``, the primary axis aligns horizontally (i.e., circles are
    visually “laid out” left–right).

    Args:
        circles: A dict whose values are :class:`Circle` objects.
        degree: Additional rotation in degrees applied after PCA alignment.

    Return:
        dict: A new dict with the same keys, where each value is a rotated
        :class:`Circle` (centers transformed; radii preserved).

    Raises:
        ValueError: If any value in ``circles`` is not a :class:`Circle`.
    """

    #print("degree", degree)

    if any(not isinstance(value, Circle) for value in circles.values()):
        raise ValueError("Can only align along axis if all values are circles.")

    centers = [circle.center for circle in circles.values()]
    radii = [circle.radius for circle in circles.values()]
    mass_center = sum(c * r for c, r in zip(centers, radii)) / sum(radii)

    # Center around the mass center and align via PCA (then rotate by 'degree')
    centered = [c - mass_center for c in centers]
    rotated = _principal_component_analysis(centered, math.radians(degree))

    # Flip if there is more mass on the negative real side (prefer “more to the right”)
    if sum(rotated).real < 0:
        rotated = [-z for z in rotated]

    # Rebuild circles with transformed centers (radii unchanged)
    return {key: Circle(center, radius) for key, center, radius in zip(circles, rotated, radii)}


def align_layouts(layout_circles_pairs: list[tuple[dict, dict]]) -> None:
    """Place multiple layouts side-by-side with a uniform horizontal gap.

    This function translates each subsequent layout (and its companion circles)
    so that their bounding boxes are laid out left-to-right with a fixed gap.

    Args:
        layout_circles_pairs:
            A list of pairs ``(layout, circles)``:
              - ``layout``: dict mapping identifiers to complex points (positions).
              - ``circles``: dict mapping identifiers to :class:`Circle` objects.
            Both dicts are modified *in place*.

    Return:
        None. The input dictionaries are translated in place.

    Notes:
        - The horizontal gap equals twice the mean radius across all provided
          ``circles`` (averaged per pair, then across pairs).
    """
    mean_radius = mean(
        mean(circle.radius for circle in circles.values() if isinstance(circle, Circle))
        for layout, circles in layout_circles_pairs
    )

    bounding_boxes = [bounding_box(layout.values()) for layout, _ in layout_circles_pairs]

    gap = mean_radius * 2
    start_x = bounding_boxes[0][1].real + gap  # start x position of the 0th component
    for (layout, circles), bb in zip(layout_circles_pairs[1:], bounding_boxes[1:]):
        dx = start_x - bb[0].real
        # translate layout points
        for key, val in layout.items():
            layout[key] = translate(val, dx)
        # translate circles
        for key, val in circles.items():
            circles[key] = translate(val, dx)
        start_x += (bb[1].real - bb[0].real) + gap