"""
Library for (numerical) geometry on the complex plane.

This module provides lightweight geometric primitives (Circle, Line, Segment,
CircularArc, OrientedCircularArc, PolySegment) and operations such as
intersections, perpendicular/tangent constructions, arc splitting/shortening,
and bounding boxes. All points are complex numbers.
"""

from __future__ import annotations

import cmath
import math
from typing import Iterable, Iterator, Optional, Sequence, Tuple, Union, List, Dict, Any

__all__ = [
    "Circle",
    "CircularArc",
    "OrientedCircularArc",
    "Line",
    "Segment",
    "BoundingBox",
    "PolySegment",
    "antipode",
    "perpendicular_line",
    "bisect",
    "tangent_line",
    "middle",
    "bisector",
    "is_angle_between",
    "perpendicular_arc_through_point",
    "perpendicular_arc",
    "circle_through_points",
    "weighted_circle_center_mean",
    "split",
    "translate",
    "bounding_box",
    "inverse_point_through_circle",
    "arc_from_circle_and_points",
    "arc_from_diameter",
]

__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

# Tolerances and numeric safeguards
DIAMETER_ERROR: float = 1e-4          # radial tolerance for "on the circle"
MIN_SEGMENT_SIZE: float = 1e-8        # minimal segment length
MIN_DETERMINANT: float = 1e-8         # minimal determinant to detect parallel lines
CIRCLE_DISTANCE_ERROR: float = 1e-6   # circle-circle relation tolerance


class Circle:
    """A circle in the complex plane."""

    def __init__(self, center: complex, radius: float) -> None:
        """
        Args:
            center: Circle center (complex).
            radius: Circle radius (non-negative).
        """
        self.center = complex(center)
        self.radius = float(radius)

    def __contains__(self, point: complex) -> bool:
        """Return True if `point` lies on the circle within tolerance."""
        return abs(abs(point - self.center) - self.radius) <= DIAMETER_ERROR

    def __mul__(self, other: Union["Circle", "Line"]) -> List[complex]:
        """Intersect with another geometric object.

        Args:
            other: A circle or a line.

        Returns:
            A list of intersection points (0, 1, or 2 points). For line-line,
            see :class:`Line`.

        Raises:
            TypeError: If the other type is unsupported.
        """
        if isinstance(other, Circle):
            return _intersection_circle_circle(self, other)
        if isinstance(other, Line):
            return _intersection_circle_line(self, other)
        raise TypeError(f"Intersection of Circle and {type(other).__name__} not supported.")

    def length(self) -> float:
        """Circumference length (2πr)."""
        return 2 * math.pi * self.radius

    def __call__(self, angle1: float, angle2: Optional[float] = None) -> Union["CircularArc", complex]:
        """Create an arc on this circle (or evaluate a point if only one angle is given).

        Args:
            angle1: First angle (radians).
            angle2: Optional second angle (radians). If provided, returns an arc
                from angle1 to angle2. If omitted, returns the point at angle1.

        Returns:
            CircularArc or complex.
        """
        if angle2 is None:
            return self.center + self.radius * (math.cos(angle1) + 1j * math.sin(angle1))
        return CircularArc(self.center, self.radius, angle1, angle2)

    def __str__(self) -> str:
        return f"Circle at {self.center:.5f} with radius {self.radius:.5f}"


class CircularArc(Circle):
    """An unoriented circular arc on a circle."""

    def __init__(self, center: complex, radius: float, theta1: float, theta2: float) -> None:
        self.theta1 = float(theta1) % (2 * math.pi)
        self.theta2 = float(theta2) % (2 * math.pi)
        super().__init__(center, radius)

    def __contains__(self, point: complex) -> bool:
        """Return True if `point` lies on this arc (on the circle and between angles)."""
        if not super().__contains__(point):
            return False
        return is_angle_between(self.theta1, cmath.phase(point - self.center), self.theta2)

    def angle(self) -> float:
        """Arc angle length (radians) in [0, 2π)."""
        return ((self.theta2 % (2 * math.pi)) - (self.theta1 % (2 * math.pi))) % (2 * math.pi)

    def length(self) -> float:
        """Arc length = radius * angle."""
        return self.angle() * self.radius

    def __call__(self, angle1: float, angle2: Optional[float] = None) -> Union["CircularArc", complex]:
        """Point on arc for a single angle; a new arc if two angles are given."""
        if angle2 is not None:
            return CircularArc(self.center, self.radius, angle1, angle2)
        if is_angle_between(self.theta1, angle1, self.theta2) or is_angle_between(self.theta2, angle1, self.theta1):
            return self.center + self.radius * (math.cos(angle1) + 1j * math.sin(angle1))
        raise ValueError(f"Angle {angle1} is not on the circular arc {self}.")

    def __neg__(self) -> "CircularArc":
        """Return the same geometric arc with reversed parameterization."""
        return CircularArc(self.center, self.radius, self.theta2, self.theta1)

    @property
    def A(self) -> complex:
        """Start point of the arc."""
        return self(self.theta1)

    @property
    def B(self) -> complex:
        """End point of the arc."""
        return self(self.theta2)

    def __str__(self) -> str:
        return (
            f"Circular arc at {self.center:.5f} with radius {self.radius:.5f} "
            f"and angles {self.theta1:.5f} and {self.theta2:.5f}"
        )


class OrientedCircularArc(CircularArc):
    """A circular arc with an orientation flag (reversed or not)."""

    def __init__(self, center: complex, radius: float, theta1: float, theta2: float, reversed: bool = False) -> None:
        self.reversed = bool(reversed)
        super().__init__(center, radius, theta1, theta2)

    def set_orientation(self, start_point: Optional[complex], end_point: Optional[complex]) -> None:
        """Set orientation so A is closer to start and B closer to end (heuristic)."""
        p1 = self.center + self.radius * (math.cos(self.theta1) + 1j * math.sin(self.theta1))
        p2 = self.center + self.radius * (math.cos(self.theta2) + 1j * math.sin(self.theta2))

        if end_point is None and start_point is not None:
            self.reversed = abs(p1 - start_point) > abs(p2 - start_point)
        elif start_point is None and end_point is not None:
            self.reversed = abs(p1 - end_point) < abs(p2 - end_point)
        elif end_point is not None and start_point is not None:
            self.reversed = (abs(p1 - end_point) + abs(p2 - start_point)) > (
                abs(p1 - start_point) + abs(p2 - end_point)
            )
        else:
            raise ValueError("start_point and/or end_point must be specified")

    def shorten(self, length: float, side: str, inplace: bool = False) -> Optional["OrientedCircularArc"]:
        """Shorten the arc by `length` from side 'A' or 'B' (w.r.t. orientation).

        Returns:
            The modified/new arc or None if fully consumed.
        """
        if self.length() <= length:
            return None

        delta = self.angle() * (length / self.length())
        if self.reversed == (side == "A"):
            # Shorten from geometric B
            if inplace:
                self.theta2 = (self.theta2 - delta) % (2 * math.pi)
                return None
            return OrientedCircularArc(self.center, self.radius, self.theta1, (self.theta2 - delta) % (2 * math.pi), reversed=self.reversed)
        else:
            # Shorten from geometric A
            if inplace:
                self.theta1 = (self.theta1 + delta) % (2 * math.pi)
                return None
            return OrientedCircularArc(self.center, self.radius, (self.theta1 + delta) % (2 * math.pi), self.theta2, reversed=self.reversed)

    @property
    def A(self) -> complex:
        """Start point respecting orientation."""
        return self(self.theta2) if self.reversed else self(self.theta1)

    @property
    def B(self) -> complex:
        """End point respecting orientation."""
        return self(self.theta1) if self.reversed else self(self.theta2)

    def __str__(self) -> str:
        base = super().__str__()
        return base + (" reversed" if self.reversed else "")


class Line:
    """An infinite line through two distinct points."""

    def __init__(self, A: complex, B: complex) -> None:
        self.A = complex(A)
        self.B = complex(B)
        if abs(self.B - self.A) < MIN_SEGMENT_SIZE:
            raise ValueError(f"Points {A} and {B} are too close to define a line.")

    def __contains__(self, point: complex) -> bool:
        """Return True if `point` lies on the line within tolerance."""
        return self.parameter_from_point(point) is not None

    def __mul__(self, other: Union["Circle", "Line"]) -> Union[List[complex], Optional[complex]]:
        """Intersection with a circle or another line.

        Returns:
            For line*circle: list of intersection points (0,1,2).
            For line*line: a single point or None if parallel.
        """
        if isinstance(other, Circle):
            return _intersection_circle_line(other, self)
        if isinstance(other, Line):
            return _intersection_line_line(self, other)
        raise TypeError(f"Intersection of Line and {type(other).__name__} not supported.")

    def parameter_from_point(self, point: complex) -> Optional[float]:
        """Parameter t for which A + t(B-A) = point, or None if not on the line."""
        t = (point - self.A) / (self.B - self.A)
        if abs(t.imag) > DIAMETER_ERROR:
            return None
        return float(t.real)

    def __neg__(self) -> "Line":
        return Line(self.B, self.A)

    @staticmethod
    def length() -> float:
        return float("inf")

    def __call__(self, t: float) -> complex:
        """Point A + t(B-A) on the line."""
        return self.A + t * (self.B - self.A)

    def __str__(self) -> str:
        return f"Line through points {self.A:.5f} and {self.B:.5f}"


class Segment(Line):
    """A line segment between A and B."""

    def __contains__(self, point: complex) -> bool:
        """Return True if `point` lies on the segment."""
        t = (point - self.A) / (self.B - self.A)
        return (abs(t.imag) <= DIAMETER_ERROR) and (0 <= t.real <= 1)

    def length(self) -> float:
        return abs(self.B - self.A)

    def set_orientation(self, start_point: Optional[complex], end_point: Optional[complex]) -> None:
        """Orient so A is closer to start_point and B closer to end_point (heuristic)."""
        if end_point is None and start_point is not None:
            if abs(self.A - start_point) > abs(self.B - start_point):
                self.A, self.B = self.B, self.A
        elif start_point is None and end_point is not None:
            if abs(self.A - end_point) < abs(self.B - end_point):
                self.A, self.B = self.B, self.A
        elif end_point is not None and start_point is not None:
            if (abs(self.A - end_point) + abs(self.B - start_point)) > (abs(self.A - start_point) + abs(self.B - end_point)):
                self.A, self.B = self.B, self.A
        else:
            raise ValueError("start_point and/or end_point must be specified")

    def shorten(self, length: float, side: str, inplace: bool = False) -> Optional["Segment"]:
        """Shorten by `length` from side 'A' or 'B'.

        Returns:
            The modified/new segment or None if fully consumed.
        """
        if self.length() <= length:
            return None
        s = (self.B - self.A) / abs(self.B - self.A)
        if side == "A":
            if inplace:
                self.A = self.A + length * s
                return None
            return Segment(self.A + length * s, self.B)
        if side == "B":
            if inplace:
                self.B = self.B - length * s
                return None
            return Segment(self.A, self.B - length * s)
        raise ValueError("side must be 'A' or 'B'")

    def __call__(self, t1: float, t2: Optional[float] = None) -> Union[complex, Optional["Segment"]]:
        """Point on the segment for t in [0,1], or subsegment if t1,t2 in [0,1]."""
        if t2 is None:
            return self.A + t1 * (self.B - self.A) if 0 <= t1 <= 1 else None
        if 0 <= t1 <= 1 and 0 <= t2 <= 1:
            return Segment(self(t1), self(t2))
        return None

    def sample(self, n: int) -> List[complex]:
        """Return n evenly spaced points on the segment (including endpoints)."""
        if n < 2:
            raise ValueError("n must be at least 2")
        return [self.A + (self.B - self.A) * i / (n - 1) for i in range(n)]

    def __str__(self) -> str:
        return f"Segment through points {self.A:.5f} and {self.B:.5f}"


class PolySegment:
    """A polyline defined by a list of complex points."""

    def __init__(self, points: Iterable[complex]) -> None:
        self.points = [complex(p) for p in points]

    def length(self) -> float:
        """Total length of the polyline."""
        return sum(abs(self.points[i + 1] - self.points[i]) for i in range(len(self.points) - 1))

    def sample(self, n: int) -> List[complex]:
        """Return n approximately evenly spaced points along the polyline."""
        if n < 2:
            raise ValueError("n must be at least 2")

        total_length = self.length()
        seg_lengths = [abs(self.points[i + 1] - self.points[i]) for i in range(len(self.points) - 1)]
        step = total_length / (n - 1)

        out = [self.points[0]]
        i = 0
        cur = self.points[0]
        remaining = step

        while len(out) < n:
            if i >= len(self.points) - 1:
                break  # rounding guard
            start = self.points[i]
            end = self.points[i + 1]
            seg_len = seg_lengths[i]
            to_end = abs(end - cur)

            if remaining <= to_end:
                direction = (end - start) / seg_len
                cur += direction * remaining
                out.append(cur)
                remaining = step
            else:
                cur = end
                remaining -= to_end
                i += 1

        if len(out) < n:
            out.append(self.points[-1])

        return out

    def __str__(self) -> str:
        return f"PolySegment through points {', '.join(str(p) for p in self.points)}"


# ==== Intersections ==========================================================

def _intersection_circle_circle(a: Circle, b: Circle) -> List[complex]:
    """Circle-circle intersection points (0,1,2), filtered to lie on both circles."""
    dist = abs(a.center - b.center)

    if dist >= a.radius + b.radius + CIRCLE_DISTANCE_ERROR:
        solutions: List[complex] = []
    elif abs(dist - (a.radius + b.radius)) <= CIRCLE_DISTANCE_ERROR:
        # Tangent externally
        solutions = [((b.center * a.radius) + (a.center * b.radius)) / (b.radius + a.radius)]
    else:
        # Two intersections
        h = (dist**2 + b.radius**2 - a.radius**2) / (2 * dist)
        m_sq = b.radius**2 - h**2
        m = math.sqrt(max(m_sq, 0.0))
        v = _normalize(a.center - b.center)  # direction from b -> a
        h_vec = h * v
        m_vec = m * (1j * v)                 # perpendicular
        solutions = [b.center + h_vec + m_vec, b.center + h_vec - m_vec]

    return [p for p in solutions if (p in a and p in b)]


def _intersection_line_line(a: Line, b: Line) -> Optional[complex]:
    """Line-line intersection (single point or None if parallel/almost parallel)."""
    det = _complex_determinant(a.B - a.A, b.A - b.B)
    if abs(det) < MIN_DETERMINANT:
        return None
    t = _complex_determinant(b.A - a.A, b.A - b.B) / det
    point = a(t)
    return point if (point in a and point in b) else None


def _intersection_circle_line(c: Circle, l: Line) -> List[complex]:
    """Circle-line (or circle-segment) intersection points."""
    s = l.B - l.A
    n = s * 1j
    # endpoints of the diameter perpendicular to the line
    e1 = c.center + c.radius * n / abs(n)
    e2 = c.center - c.radius * n / abs(n)
    # midpoint of the chord = intersection of the line with the perpendicular diameter
    p = _intersection_line_line(Line(l.A, l.B), Segment(e1, e2))
    if p is None:
        return []
    d = abs(p - c.center)
    m_sq = c.radius * c.radius - d * d
    if m_sq < 0:
        return []
    m = math.sqrt(m_sq)
    results = [p + m * s / abs(s), p - m * s / abs(s)] if m != 0 else [p]
    return [pt for pt in results if (pt in c and pt in l)]


# ==== Utilities ==============================================================

def _normalize(z: complex) -> complex:
    """Normalize complex vector z to unit length."""
    return z / abs(z)


def _complex_determinant(z: complex, w: complex) -> float:
    """Return z.real*w.imag - z.imag*w.real using an efficient form."""
    return (z.conjugate() * w).imag


def is_angle_between(theta1: float, theta2: float, theta3: float) -> bool:
    """Return True if theta2 is between theta1 and theta3 (mod 2π)."""
    theta1 %= 2 * math.pi
    theta2 %= 2 * math.pi
    theta3 %= 2 * math.pi
    if theta1 <= theta3:
        return theta1 <= theta2 <= theta3
    return theta2 >= theta1 or theta2 <= theta3


def perpendicular_line(l: Line, p: complex) -> Line:
    """Line through p perpendicular to l."""
    return Line(p, p + 1j * (l.B - l.A))


def tangent_line(c: Circle, p: complex) -> Line:
    """Tangent line to circle c at point p (or perpendicular to radius if p not on c)."""
    return perpendicular_line(Line(c.center, p), p)


def antipode(circle: Circle, point: complex) -> complex:
    """Antipodal point of `point` through `circle.center`."""
    return 2 * circle.center - point


def inverse_point_through_circle(circle: Circle, point: complex) -> complex:
    """Invert a point w.r.t. a circle.

    Args:
        circle: Circle of inversion.
        point: Point to invert.

    Returns:
        The inverse point as complex.
    """
    d = abs(point - circle.center)
    if d == 0:
        # Convention: leave it at center (could also raise)
        return circle.center
    return circle.center + (circle.radius**2 / d**2) * (point - circle.center)


def perpendicular_arc_through_point(circle: Circle, circle_point: complex, point: complex) -> Union[CircularArc, Segment]:
    """Arc through `circle_point` and `point` perpendicular to `circle` at `circle_point`."""
    tangent = tangent_line(circle, circle_point)
    segment = Segment(circle_point, point)
    seg_bis = bisector(segment)
    center = tangent * seg_bis  # intersection of lines
    if center is None:
        return Segment(circle_point, point)
    theta1 = cmath.phase(circle_point - center) % (2 * math.pi)
    theta2 = cmath.phase(point - center)
    # choose shorter direction
    if ((theta2 - theta1) % (2 * math.pi)) > math.pi:
        theta1, theta2 = theta2, theta1
    return CircularArc(center, abs(center - circle_point), theta1, theta2)


def perpendicular_arc(circle: Circle, circle1: Circle, circle2: Circle) -> Union[CircularArc, Segment]:
    """Arc inside `circle` connecting its intersections with `circle1` and `circle2`, perpendicular to `circle`."""
    p1 = circle * circle1
    p2 = circle * circle2
    if len(p1) == 0 or len(p2) == 0:
        raise ValueError("No intersection point when computing perpendicular arc.")
    if len(p1) == 2 or len(p2) == 2:
        raise ValueError("Two intersection points (tangent ambiguity) when computing perpendicular arc.")
    i1, i2 = p1[0], p2[0]
    mid = 0.5 * (i1 + i2)

    # If diameter, return segment
    if abs(mid - circle.center) <= MIN_SEGMENT_SIZE:
        return Segment(i1, i2)

    inv_mid = inverse_point_through_circle(circle, mid)
    arc = CircularArc(inv_mid, abs(inv_mid - i1), cmath.phase(i1 - inv_mid), cmath.phase(i2 - inv_mid))
    # take the shorter arc
    if ((arc.theta2 - arc.theta1) % (2 * math.pi)) > math.pi:
        arc.theta1, arc.theta2 = arc.theta2, arc.theta1
    return arc


def arc_from_circle_and_points(circle: Circle, point1: complex, point2: complex) -> CircularArc:
    """Arc on `circle` from `point1` to `point2`."""
    if point1 not in circle or point2 not in circle:
        raise ValueError("Points must lie on the circle.")
    return CircularArc(circle.center, abs(circle.center - point1), cmath.phase(point1 - circle.center), cmath.phase(point2 - circle.center))


def arc_from_diameter(point1: complex, point2: complex) -> CircularArc:
    """Arc on the circle having diameter (point1, point2), from point1 to point2."""
    return arc_from_circle_and_points(Circle((point1 + point2) / 2, abs(point1 - point2) / 2), point1, point2)

# Backward-compatibility alias (typo in old API)
arc_from_diamater = arc_from_diameter


def weighted_circle_center_mean(circle1: Circle, circle2: Circle) -> complex:
    """Weighted mean of centers proportional to opposite radii (heuristic)."""
    rsum = circle1.radius + circle2.radius
    if rsum == 0:
        return (circle1.center + circle2.center) / 2
    return circle1.center * (circle2.radius / rsum) + circle2.center * (circle1.radius / rsum)


def orient_arc(g: Union[CircularArc, Segment], start_point: Optional[complex] = None, end_point: Optional[complex] = None) -> Union[OrientedCircularArc, Segment]:
    """Return an oriented copy of `g` according to start/end heuristics."""
    if isinstance(g, CircularArc):
        arc = OrientedCircularArc(g.center, g.radius, g.theta1, g.theta2, reversed=False)
        arc.set_orientation(start_point, end_point)
        return arc
    if isinstance(g, Segment):
        seg = Segment(g.A, g.B)
        seg.set_orientation(start_point, end_point)
        return seg
    raise TypeError("Can only orient a CircularArc or a Segment.")


def split(g: Union[CircularArc, Segment], point: complex) -> Tuple[Union[CircularArc, Segment], Union[CircularArc, Segment]]:
    """Split an arc/segment at a point lying on it, returning two pieces."""
    if isinstance(g, Segment):
        return Segment(g.A, point), Segment(point, g.B)
    if isinstance(g, CircularArc):
        angle = cmath.phase(point - g.center)
        return CircularArc(g.center, g.radius, g.theta1, angle), CircularArc(g.center, g.radius, angle, g.theta2)
    raise TypeError("Can only split a CircularArc or a Segment.")


def bisect(g: Union[CircularArc, Segment]) -> Tuple[Union[CircularArc, Segment], Union[CircularArc, Segment]]:
    """Split a Segment or CircularArc into two equal halves."""
    if isinstance(g, Segment):
        mid = 0.5 * (g.A + g.B)
        return Segment(g.A, mid), Segment(mid, g.B)
    if isinstance(g, CircularArc):
        angle = 0.5 * (g.theta1 + g.theta2)
        # adjust to ensure "middle" lies on the shorter half
        a1 = abs((g.theta1 - angle) % (2 * math.pi))
        if a1 > math.pi / 2 and a1 > math.pi / 2:
            angle = (angle + math.pi) % (2 * math.pi)
        return CircularArc(g.center, g.radius, g.theta1, angle), CircularArc(g.center, g.radius, angle, g.theta2)
    raise TypeError("Can only bisect a CircularArc or a Segment.")


def bisector(s: Segment) -> Line:
    """Perpendicular bisector of a segment."""
    return perpendicular_line(s, 0.5 * (s.A + s.B))


def middle(g: Union[CircularArc, Segment, complex]) -> complex:
    """Geometric middle point of a Segment or CircularArc, or the point itself."""
    if isinstance(g, Segment):
        return 0.5 * (g.A + g.B)
    if isinstance(g, CircularArc):
        angle = 0.5 * (g.theta1 + g.theta2)
        a1 = abs((g.theta1 - angle) % (2 * math.pi))
        if a1 > math.pi / 2 and a1 > math.pi / 2:
            return g((angle + math.pi) % (2 * math.pi))
        return g(angle)
    if isinstance(g, complex):
        return g
    raise TypeError("Unsupported type for middle(); expected Segment, CircularArc, or complex.")


def circle_through_points(A: complex, B: complex, C: complex) -> Optional[Circle]:
    """Circle through three points A, B, C (or None if collinear)."""
    ab = Segment(A, B)
    bc = Segment(B, C)
    center = _intersection_line_line(bisector(ab), bisector(bc))
    if center is None:
        return None
    # average distances (robust-ish)
    radius = (abs(center - A) + abs(center - B) + abs(center - C)) / 3
    return Circle(center, radius)


class BoundingBox:
    """Axis-aligned bounding box for basic primitives."""

    def __init__(self, g: Optional[Union[CircularArc, Circle, Segment, Line, complex]] = None) -> None:
        if g is None:
            self.bottom_left = 0 + 0j
            self.top_right = 0 + 0j
            return

        if isinstance(g, CircularArc):
            angles = [0, math.pi / 2, math.pi, 3 * math.pi / 2]
            pts = [g(g.theta1), g(g.theta2)]
            for beta in angles:
                if is_angle_between(g.theta1, beta, g.theta2):
                    pts.append(g(beta))
            self.bottom_left = min(p.real for p in pts) + 1j * min(p.imag for p in pts)
            self.top_right = max(p.real for p in pts) + 1j * max(p.imag for p in pts)
        elif isinstance(g, Circle):
            self.bottom_left = g.center - (1 + 1j) * g.radius
            self.top_right = g.center + (1 + 1j) * g.radius
        elif isinstance(g, Segment):
            self.bottom_left = min(g.A.real, g.B.real) + 1j * min(g.A.imag, g.B.imag)
            self.top_right = max(g.A.real, g.B.real) + 1j * max(g.A.imag, g.B.imag)
        elif isinstance(g, Line):
            # Axis-aligned infinite lines are not bounded; keep zero box.
            self.bottom_left = 0 + 0j
            self.top_right = 0 + 0j
        elif isinstance(g, complex):
            self.bottom_left = complex(g)
            self.top_right = complex(g)
        else:
            raise ValueError("Unsupported type for BoundingBox.")

    def make_square(self) -> None:
        """Expand to the smallest square that contains the current box."""
        size_x = self.top_right.real - self.bottom_left.real
        size_y = self.top_right.imag - self.bottom_left.imag
        size = max(size_x, size_y)
        dx = (size - size_x) / 2
        dy = (size - size_y) / 2
        self.bottom_left -= dx + 1j * dy
        self.top_right += dx + 1j * dy

    def add_padding(self, units: Optional[float] = None, fraction: Optional[float] = None) -> None:
        """Pad the box by absolute units and/or by a fraction of its size."""
        if units is None and fraction is None:
            raise ValueError("Specify `units` and/or `fraction` for padding.")
        if units is not None:
            self.bottom_left -= units + 1j * units
            self.top_right += units + 1j * units
        if fraction is not None:
            padding = (self.top_right - self.bottom_left) * fraction
            self.bottom_left -= padding
            self.top_right += padding

    def __repr__(self) -> str:
        return f"BoundingBox(bottom_left={self.bottom_left}, top_right={self.top_right})"

    def __ior__(self, other: "BoundingBox") -> "BoundingBox":
        """In-place union with another bounding box."""
        self.bottom_left = min(self.bottom_left.real, other.bottom_left.real) + 1j * min(
            self.bottom_left.imag, other.bottom_left.imag
        )
        self.top_right = max(self.top_right.real, other.top_right.real) + 1j * max(
            self.top_right.imag, other.top_right.imag
        )
        return self


def translate(element: Union[Segment, Line, Circle, PolySegment, CircularArc, OrientedCircularArc, complex, float, int, None], displacement: complex):
    """Translate a geometric element by a complex displacement."""
    if isinstance(element, Segment):
        return Segment(element.A + displacement, element.B + displacement)
    if isinstance(element, Line):
        return Line(element.A + displacement, element.B + displacement)
    if isinstance(element, Circle):
        return Circle(element.center + displacement, element.radius)
    if isinstance(element, PolySegment):
        return PolySegment([p + displacement for p in element.points])
    if isinstance(element, CircularArc):
        return CircularArc(element.center + displacement, element.radius, element.theta1, element.theta2)
    if isinstance(element, OrientedCircularArc):
        return OrientedCircularArc(element.center + displacement, element.radius, element.theta1, element.theta2, element.reversed)
    if isinstance(element, (complex, float, int)):
        return complex(element) + displacement
    if element is None:
        return None
    raise TypeError(f"Translation is not defined for {type(element).__name__}.")


def bounding_box(g: Union[CircularArc, Segment, Circle, complex, Iterable]) -> Tuple[complex, complex]:
    """Compute an axis-aligned bounding box (min_corner, max_corner).

    For iterables, returns the union over elements.
    """
    if isinstance(g, CircularArc):
        min_x, max_x = min(g.A.real, g.B.real), max(g.A.real, g.B.real)
        min_y, max_y = min(g.A.imag, g.B.imag), max(g.A.imag, g.B.imag)
        for angle in (0, math.pi / 2, math.pi, 3 * math.pi / 2):
            if is_angle_between(g.theta1, angle, g.theta2):
                p = g(angle)
                min_x, max_x = min(min_x, p.real), max(max_x, p.real)
                min_y, max_y = min(min_y, p.imag), max(max_y, p.imag)
        return complex(min_x, min_y), complex(max_x, max_y)

    if isinstance(g, Segment):
        return complex(min(g.A.real, g.B.real), min(g.A.imag, g.B.imag)), complex(
            max(g.A.real, g.B.real), max(g.A.imag, g.B.imag)
        )

    if isinstance(g, Circle):
        return g.center - (1 + 1j) * g.radius, g.center + (1 + 1j) * g.radius

    if g is None:
        return 0 + 0j, 0 + 0j

    if isinstance(g, complex):
        return complex(g), complex(g)

    # Assume iterable of geometries
    bbs = [bounding_box(item) for item in g]  # type: ignore[arg-type]
    min_corner = complex(min(bb[0].real for bb in bbs), min(bb[0].imag for bb in bbs))
    max_corner = complex(max(bb[1].real for bb in bbs), max(bb[1].imag for bb in bbs))
    return min_corner, max_corner


def angle_between(z1: complex, z2: complex, z3: complex) -> float:
    """Unsigned angle ∠z1 z2 z3 in radians."""
    v1 = z1 - z2
    v2 = z3 - z2
    return abs(cmath.phase(v2 / v1))


if __name__ == "__main__":
    pass
