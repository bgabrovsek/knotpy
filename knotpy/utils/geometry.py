"""
Library for (numerical) geometry.

This module provides basic geometric primitives—circles, circular arcs,
lines, line segments, polylines—and common operations on them (intersection,
orientation, bisectors, perpendicular constructs, circle packing helpers, etc.).
All coordinates are represented as complex numbers.
"""

import math
import cmath

__all__ = [
    "Circle",
    "CircularArc",
    "Line",
    "Segment",
    "BoundingBox",
    "PolySegment",
    "antipode",
    "arc_from_diameter",
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
]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


DIAMETER_ERROR = 0.0001     # tolerance for testing whether a point lies on a circle
MIN_SEGMENT_SIZE = 1E-8     # smallest distance still considered a segment
MIN_DETERMINANT = 1E-8      # tolerance for treating lines as parallel
CIRCLE_DISTANCE_ERROR = 1E-6  # tolerance for circle-circle distance (tangent/disjoint/intersecting)


class Circle:
    """
    Representation of a geometric circle in the complex plane.

    Attributes:
        center: The center of the circle (complex number).
        radius: The radius of the circle (float).
    """

    def __init__(self, center: complex, radius: float):
        """
        Create a circle characterized by a center point and a radius.

        Args:
            center: Complex number representing the circle's center.
            radius: Radius of the circle.
        """
        self.center = center
        self.radius = radius

    def __contains__(self, point: complex) -> bool:
        """
        Check whether a given point lies on the circle (within a small tolerance).

        Args:
            point: Complex coordinate of the point to test.

        Returns:
            True if the point lies on the circle; False otherwise.
        """
        return abs(abs(point - self.center) - self.radius) <= DIAMETER_ERROR

    def __mul__(self, other):
        """
        Compute the intersection between the circle and another geometric object.

        Args:
            other: A `Circle` or `Line`.

        Returns:
            A list of intersection points (possibly empty or of length 1/2),
            depending on the configuration.

        Raises:
            TypeError: If `other` is not a `Circle` or `Line`.
        """
        if isinstance(other, Circle):
            return _intersection_circle_circle(self, other)
        if isinstance(other, Line):
            return _intersection_circle_line(self, other)
        raise TypeError(f"Intersection of a circle and {type(other)} not supported")

    def length(self):
        """Return the circumference of the circle."""
        return 2 * math.pi * self.radius

    def __call__(self, angle1, angle2):
        """
        Return the circular arc between two angles on this circle.

        Args:
            angle1: Starting angle (radians).
            angle2: Ending angle (radians).

        Returns:
            `CircularArc` defined by this circle and the two angles.
        """
        return CircularArc(self.center, self.radius, angle1, angle2)

    def __str__(self):
        return f"Circle at {self.center:.5f} with radius {self.radius:.5f}"


class CircularArc(Circle):
    """A circular arc defined by a center, radius, and two angles (theta1 → theta2)."""

    def __init__(self, center, radius, theta1, theta2):
        self.theta1 = theta1 % (2 * math.pi)
        self.theta2 = theta2 % (2 * math.pi)
        super().__init__(center, radius)

    def __contains__(self, point):
        """Check whether a point lies on this circular arc (within tolerance)."""
        if not super().__contains__(point):
            return False
        return is_angle_between(self.theta1, cmath.phase(point - self.center), self.theta2)

    def angle(self):
        """Angular span of the arc in radians (in [0, 2π))."""
        return ((self.theta2 % (2 * math.pi)) - (self.theta1 % (2 * math.pi))) % (2 * math.pi)

    def length(self):
        """Arc length (radius × angle)."""
        return self.angle() * self.radius

    def __call__(self, angle1, angle2=None):
        """
        If `angle2` is given, return a new arc from `angle1` to `angle2`.
        Otherwise, return the point on the arc at angle `angle1` (if on arc).
        """
        if angle2 is not None:
            return CircularArc(self.center, self.radius, angle1, angle2)

        if is_angle_between(self.theta1, angle1, self.theta2) or is_angle_between(self.theta2, angle1, self.theta1):
            return self.center + self.radius * math.cos(angle1) + 1j * self.radius * math.sin(angle1)
        else:
            raise ValueError(f"The angle {angle1} does not lie on the circular arc {self}")

    def __neg__(self):
        """Reverse the arc direction (swap theta1 and theta2)."""
        return CircularArc(self.center, self.radius, self.theta2, self.theta1)

    @property
    def A(self):
        """Start point of the arc."""
        return self(self.theta1)

    @property
    def B(self):
        """End point of the arc."""
        return self(self.theta2)

    def __str__(self):
        return (
            f"Circular arc at {self.center:.5f} with radius {self.radius:.5f} "
            f"and angles {self.theta1:.5f} and {self.theta2:.5f}"
        )


class OrientedCircularArc(CircularArc):
    """Circular arc with an orientation flag for start/end selection."""

    def __init__(self, center, radius, theta1, theta2, reversed=False):
        self.reversed = reversed
        super().__init__(center, radius, theta1, theta2)

    def set_orientation(self, start_point, end_point):
        """
        Set the orientation so that the point at angle `theta1` is closer to
        `start_point` and the point at `theta2` is closer to `end_point`.
        """
        point1 = self.center + self.radius * math.cos(self.theta1) + 1j * self.radius * math.sin(self.theta1)
        point2 = self.center + self.radius * math.cos(self.theta2) + 1j * self.radius * math.sin(self.theta2)

        if end_point is None:
            self.reversed = abs(point1 - start_point) > abs(point2 - start_point)
        elif start_point is None:
            self.reversed = abs(point1 - end_point) < abs(point2 - end_point)
        elif end_point is not None and start_point is not None:
            self.reversed = (
                abs(point1 - end_point) + abs(point2 - start_point)
                > abs(point1 - start_point) + abs(point2 - end_point)
            )
        else:
            raise ValueError("start_point and/or end_point must be specified")

    def shorten(self, length, side, inplace=False):
        """Shorten arc from side 'A' (start) or 'B' (end)."""
        if self.length() <= length:
            return None
        if side not in ['A', 'B']:
            raise ValueError(f"side must be 'A' or 'B', not {side}")

        delta = ((self.theta2 - self.theta1) % (2 * math.pi)) * length / self.length()

        if self.reversed == (side == 'A'):
            if inplace:
                self.theta2 = (self.theta2 - delta) % (2 * math.pi)
            else:
                return OrientedCircularArc(
                    self.center, self.radius, self.theta1, (self.theta2 - delta) % (2 * math.pi), reversed=self.reversed
                )
        else:
            if inplace:
                self.theta1 = self.theta1 + delta
            else:
                return OrientedCircularArc(self.center, self.radius, self.theta1 + delta, self.theta2, reversed=self.reversed)

    @property
    def A(self):
        """Start point respecting the `reversed` flag."""
        return self(self.theta2) if self.reversed else self(self.theta1)

    @property
    def B(self):
        """End point respecting the `reversed` flag."""
        return self(self.theta1) if self.reversed else self(self.theta2)

    def __str__(self):
        return (
            f"Oriented Circular arc at {self.center:.5f} with radius {self.radius:.5f} "
            f"and angles {self.theta1:.5f} and {self.theta2:.5f}" + (" reversed" if self.reversed else "")
        )


class Line:
    """An infinite line determined by two points A and B."""

    def __init__(self, A, B):
        self.A = A
        self.B = B
        if abs(self.B - self.A) < MIN_SEGMENT_SIZE:
            raise ValueError(f"Points {A} and {B} too close to each other.")

    def __contains__(self, point):
        """
        Check whether the point lies on the line.

        The point lies on the line through A and B if `(point - A)` is a real
        multiple of `(B - A)`.
        """
        return self.parameter_from_point(point) is not None

    def __mul__(self, other):
        """Intersection between geometric objects (circle/line)."""
        if isinstance(other, Circle):
            return _intersection_circle_line(other, self)
        if isinstance(other, Line):
            return _intersection_line_line(self, other)

    def parameter_from_point(self, point):
        """For the line `T = A + t(B-A)`, return `t` such that `T = point` (if on the line)."""
        t = (point - self.A) / (self.B - self.A)
        if abs(t.imag) > DIAMETER_ERROR:
            return None
        return t.real

    def __neg__(self):
        """Reverse direction (swap endpoints)."""
        return Line(self.B, self.A)

    @staticmethod
    def length(self):
        """Infinite line has infinite length."""
        return float("inf")

    def __call__(self, t):
        """Point on the line `A + t * (B - A)`."""
        return self.A + t * (self.B - self.A)

    def __str__(self):
        return f"Line through points {self.A:.5f} and {self.B:.5f}"


class Segment(Line):
    """A finite line segment from A to B."""

    def __contains__(self, point):
        """
        Check whether the point lies on this segment.

        It must lie on the supporting line and the parameter `t` must be in [0, 1].
        """
        t = (point - self.A) / (self.B - self.A)
        return abs(t.imag) <= DIAMETER_ERROR and 0 <= t.real <= 1

    def length(self):
        """Length of the segment (|B - A|)."""
        return abs(self.B - self.A)

    def set_orientation(self, start_point, end_point):
        """
        Set orientation so that A is closer to `start_point` and B closer to `end_point`.
        """
        if end_point is None:
            if abs(self.A - start_point) > abs(self.B - start_point):
                self.A, self.B = self.B, self.A
        elif start_point is None:
            if abs(self.A - end_point) < abs(self.B - end_point):
                self.A, self.B = self.B, self.A
        elif end_point is not None and start_point is not None:
            if abs(self.A - end_point) + abs(self.B - start_point) > abs(self.A - start_point) + abs(self.B - end_point):
                self.A, self.B = self.B, self.A
        else:
            raise ValueError("start_point and/or end_point must be specified")

    def shorten(self, length, side, inplace=False):
        """Shorten by `length` on side 'A' or 'B'."""
        if self.length() <= length:
            return None
        s = (self.B - self.A) / abs(self.B - self.A)  # unit direction
        if side == 'A':
            if inplace:
                self.A = self.A + length * s
            else:
                return Segment(self.A + length * s, self.B)
        elif side == 'B':
            if inplace:
                self.B = self.A + length * s
            else:
                return Segment(self.A, self.B - length * s)
        else:
            raise ValueError("side must be 'A' or 'B'")

    def __call__(self, t1, t2=None):
        """
        If only `t1` is given, return the point at parameter `t1` (0 ≤ t1 ≤ 1).
        If both `t1` and `t2` are given, return the subsegment between them if
        both lie in [0, 1]; otherwise `None`.
        """
        if t2 is None:
            return self.A + t1 * (self.B - self.A) if 0 <= t1 <= 1 else None
        else:
            if 0 <= t1 <= 1 and 0 <= t2 <= 1:
                return Segment(self(t1), self(t2))
            else:
                return None

    def sample(self, n):
        """Split the segment into `n` evenly spaced complex points (inclusive)."""
        if n < 2:
            raise ValueError("n must be at least 2")
        return [self.A + (self.B - self.A) * i / (n - 1) for i in range(n)]

    def __str__(self):
        return f"Segment through points {self.A:.5f} and {self.B:.5f}"


class PolySegment:
    """A polyline segment defined by a list of complex points."""

    def __init__(self, points):
        self.points = [complex(p) for p in points]

    def length(self):
        """Total length of the polyline."""
        return sum(abs(self.points[i + 1] - self.points[i]) for i in range(len(self.points) - 1))

    def sample(self, n):
        """
        Sample `n` points along the polyline at (approximately) equal arc-length spacing,
        including endpoints.
        """
        if n < 2:
            raise ValueError("n must be at least 2")

        total_length = self.length()
        segment_lengths = [abs(self.points[i + 1] - self.points[i]) for i in range(len(self.points) - 1)]
        dist = total_length / (n - 1)

        result = [self.points[0]]
        i = 0
        current_pos = self.points[0]
        remaining = dist

        while len(result) < n:
            if i >= len(self.points) - 1:
                break  # in case we run out of segments due to rounding

            start = self.points[i]
            end = self.points[i + 1]
            seg_length = segment_lengths[i]

            to_end = abs(end - current_pos)

            if remaining <= to_end:
                direction = (end - start) / seg_length
                current_pos += direction * remaining
                result.append(current_pos)
                remaining = dist
            else:
                current_pos = end
                remaining -= to_end
                i += 1

        if len(result) < n:
            result.append(self.points[-1])

        return result

    def __str__(self):
        return f"PolySegment through points {', '.join(str(p) for p in self.points)}"


##### INTERSECTION #############################################################

def _intersection_circle_circle(a: Circle, b: Circle):
    """
    Find intersection points of two circles in the complex plane.

    Let d be the distance between centers. Let the intersection points be P1, P2,
    and let 2m be the distance between P1 and P2 (the chord length). If h is the
    distance from circle b's center to the midpoint of P1–P2, then:
      h^2 + m^2 = r_b^2  and  (d - h)^2 + m^2 = r_a^2.
    """
    dist = abs(a.center - b.center)

    if dist >= a.radius + b.radius + CIRCLE_DISTANCE_ERROR:
        # Disjoint circles
        solutions = []

    elif abs(dist - b.radius - a.radius) <= CIRCLE_DISTANCE_ERROR:
        # Tangent circles (single touching point along the line of centers)
        solutions = [(b.center * a.radius + a.center * b.radius) / (b.radius + a.radius)]

    else:
        # Two intersections
        h = (dist ** 2 + b.radius ** 2 - a.radius ** 2) / (2 * dist)
        m = math.sqrt(b.radius ** 2 - h ** 2)
        v = _normalize(a.center - b.center)
        h = h * v
        m = m * (1j * v)
        solutions = [b.center + h + m, b.center + h - m]

    # Filter to ensure the points lie on both circles (important for arcs).
    return [point for point in solutions if point in a and point in b]


def _intersection_line_line(a: Line, b: Line):
    """
    Compute intersection of two lines (or segments).

    Returns:
        The intersection point if it exists and lies on both objects; otherwise `None`.

    Method:
        Solve `a.A + t(a.B - a.A) = b.A + t'(b.B - b.A)` using Cramer's rule.
    """
    det = _complex_determinant(a.B - a.A, b.A - b.B)
    if abs(det) < MIN_DETERMINANT:
        return None
    else:
        t = _complex_determinant(b.A - a.A, b.A - b.B) / det
        point = a(t)
        if point is None:
            return None
        return point if point is None or (point in a and point in b) else None


def _intersection_circle_line(c: Circle, l: Line):
    """
    Compute intersection between a circle and a line (or segment).

    Args:
        c: `Circle`
        l: `Line` or `Segment`

    Returns:
        List of intersection point(s) (0, 1, or 2), filtered to lie on both.
    """
    s = l.B - l.A               # direction vector along the line
    n = s * 1j                  # perpendicular vector
    # Diameter endpoints along the perpendicular to the line through the circle center.
    e1 = c.center + c.radius * n / abs(n)
    e2 = c.center - c.radius * n / abs(n)
    # Midpoint of the chord cut by the line:
    p = _intersection_line_line(Line(l.A, l.B), Segment(e1, e2))
    if p is None:
        return []
    d = abs(p - c.center)
    m = math.sqrt(c.radius * c.radius - d * d)  # half chord length

    result = [p + m * s / abs(s), p - m * s / abs(s)] if m != 0 else [p]
    return [point for point in result if point in c and point in l]


##### HELPERS & GEOMETRIC OPERATIONS ###########################################

def _normalize(z: complex) -> complex:
    """Normalize a complex number: z / |z|."""
    return z / abs(z)

def _complex_determinant(z: complex, w: complex):
    """Return z.real * w.imag - z.imag * w.real (imaginary part of z̄w)."""
    return (z.conjugate() * w).imag

def is_angle_between(theta1: float, theta2: float, theta3: float) -> bool:
    """
    Check whether angle `theta2` lies between `theta1` and `theta3` on the circle (mod 2π).
    """
    theta1 = theta1 % (2 * math.pi)
    theta2 = theta2 % (2 * math.pi)
    theta3 = theta3 % (2 * math.pi)

    if theta1 <= theta3:
        return theta1 <= theta2 <= theta3
    else:
        return theta1 <= theta2 or theta2 <= theta3


def perpendicular_line(l: Line, p: complex):
    """Return a line through `p` perpendicular to line `l`."""
    return Line(p, p + 1j * (l.B - l.A))

def tangent_line(c: Circle, p: complex):
    """
    Return the line tangent to circle `c` at point `p`.

    If `p` is not on the circle, this returns the line perpendicular to the radius
    through the center and `p`.
    """
    return perpendicular_line(Line(c.center, p), p)

def antipode(circle, point):
    """
    Return the antipodal point: reflection of `point` through the circle's center.
    """
    # TODO: duplicate of a potential class method
    return circle.center - (point - circle.center)

def inverse_point_through_circle(circle, point):
    """
    Perform inversion of a point with respect to a circle.

    Args:
        circle: A `Circle` with center `C` and radius `r`.
        point: Point `P` to invert (complex).

    Returns:
        The inverse point `P'` such that |CP| * |CP'| = r^2.
    """
    d = abs(circle.center - point)
    return circle.center + (circle.radius ** 2 / d ** 2) * (point - circle.center)

def perpendicular_arc_through_point(circle, circle_point, point):
    """
    Return an arc that is:
      • perpendicular to `circle` at `circle_point`,
      • starts at `circle_point` and goes through `point`,
      • and (if `point` lies on the circle) is perpendicular there as well.
    """
    tangent = tangent_line(circle, circle_point)
    segment = Segment(circle_point, point)
    seg_bis = bisector(segment)
    center = tangent * seg_bis  # intersection

    if center is None:  # no intersection ⇒ degenerate to a straight segment
        return Segment(circle_point, point)

    theta1 = cmath.phase(circle_point - center) % (2 * math.pi)
    theta2 = cmath.phase(point - center)
    angle_diff = (theta2 - theta1) % (2 * math.pi)
    if angle_diff > math.pi:
        theta1, theta2 = theta2, theta1

    return CircularArc(center, abs(center - circle_point), theta1, theta2)

def perpendicular_arc(circle, circle1, circle2):
    """
    Return the circular arc inside `circle` that starts at `circle ∩ circle1`
    and ends at `circle ∩ circle2`, and is perpendicular to all three circles.

    Circles are given by `(center, radius)` pairs. The arc is constructed by
    inverting the midpoint of the endpoints through `circle`, which yields the
    center of the perpendicular circle; the shorter arc is returned. If the
    arc degenerates to a diameter, a segment is returned.
    """
    order = []
    approx = False
    if order is None:
        order = []
    else:
        order.clear()

    point1 = circle * circle1
    point2 = circle * circle2
    if len(point1) == 0 or len(point2) == 0:
        raise ValueError("No intersection point computing perpendicular arc")
    if len(point1) == 2 or len(point2) == 2:
        raise ValueError("two intersection points of tangent circles")
        print("Warning: two intersection points of tangent circles")
    point1 = point1[0]
    point2 = point2[0]
    midpoint = 0.5 * (point1 + point2)

    # If the arc is not a diameter, invert the midpoint through `circle`.
    if abs(midpoint - circle.center) > MIN_SEGMENT_SIZE:
        inv_midpoint = inverse_point_through_circle(circle, midpoint)
        inv_arc = CircularArc(
            inv_midpoint,
            abs(inv_midpoint - point1),
            cmath.phase(point1 - inv_midpoint),
            cmath.phase(point2 - inv_midpoint),
        )

        # Keep the shorter of the two possible arcs.
        if (inv_arc.theta2 - inv_arc.theta1) % (2 * math.pi) > math.pi:
            inv_arc.theta1, inv_arc.theta2 = inv_arc.theta2, inv_arc.theta1

        return inv_arc
    else:
        # Diameter ⇒ return a straight segment.
        return Segment(point1, point2)

def arc_from_circle_and_points(circle, point1, point2):
    """Return the circular arc on `circle` from `point1` to `point2`."""
    if point1 not in circle and point2 not in circle:
        raise ValueError("The points do not lie on the circle")
    return CircularArc(
        circle.center,
        abs(circle.center - point1),
        cmath.phase(point1 - circle.center),
        cmath.phase(point2 - circle.center),
    )

def arc_from_diameter(point1, point2):
    """Return the circular arc determined by the diameter endpoints `point1`, `point2`."""
    return arc_from_circle_and_points(Circle((point1 + point2) / 2, abs(point1 - point2) / 2), point1, point2)

def weighted_circle_center_mean(circle1: Circle, circle2: Circle):
    """Compute a weighted mean of centers so that intersections scale proportionally."""
    radii = circle1.radius + circle2.radius
    return circle1.center * (circle2.radius / radii) + circle2.center * (circle1.radius / radii)


def orient_arc(g: CircularArc | Segment, start_point=None, end_point=None):
    """
    From an unoriented arc/segment, return an oriented one so that:
      • point A is (on average) closer to `start_point`, and
      • point B is (on average) closer to `end_point`.
    """
    if type(g) is CircularArc:
        arc = OrientedCircularArc(g.center, g.radius, g.theta1, g.theta2, reversed=False)
        arc.set_orientation(start_point, end_point)
        return arc
    elif type(g) is Segment:
        segment = Segment(g.A, g.B)
        segment.set_orientation(start_point, end_point)
        return segment
    raise TypeError("Can only orient an arc or a segment.")

def split(g, point):
    """Split an arc/segment `g` at `point` (which must lie on `g`)."""
    if isinstance(g, Segment):
        return Segment(g.A, point), Segment(point, g.B)
    if isinstance(g, CircularArc):
        angle = cmath.phase(point - g.center)
        return CircularArc(g.center, g.radius, g.theta1, angle), CircularArc(g.center, g.radius, angle, g.theta2)
    raise TypeError("Can only split an arc or a segment.")

def bisect(g):
    """Split a `Segment`/`CircularArc` into two equal halves."""
    if isinstance(g, Segment):
        return Segment(g.A, 0.5 * (g.A + g.B)), Segment(0.5 * (g.A + g.B), g.B)

    if isinstance(g, CircularArc):
        angle = 0.5 * (g.theta1 + g.theta2)
        if abs(g.theta1 - angle) % (2 * math.pi) > math.pi / 2 and abs(g.theta1 - angle) % (2 * math.pi) > math.pi / 2:
            angle = angle + math.pi
        return (CircularArc(g.center, g.radius, g.theta1, angle), CircularArc(g.center, g.radius, angle, g.theta2))

    raise TypeError("Can only bisect an arc or a segment.")

def bisector(s: Segment) -> Line:
    """Return the perpendicular bisector line of the segment."""
    return perpendicular_line(s, 0.5 * (s.A + s.B))

def middle(g) -> complex:
    """Return the geometric center of a segment or arc (or the point if already complex)."""
    if isinstance(g, Segment):
        return 0.5 * (g.A + g.B)

    if isinstance(g, CircularArc):
        angle = 0.5 * (g.theta1 + g.theta2)
        if abs(g.theta1 - angle) % (2 * math.pi) > math.pi / 2 and abs(g.theta1 - angle) % (2 * math.pi) > math.pi / 2:
            return g(angle + math.pi)
        else:
            return g(angle)

    if isinstance(g, complex):
        return g

    raise TypeError("Can only bisect an arc or a segment.")

def circle_through_points(A, B, C):
    """Return a circle through three non-collinear points A, B, C."""
    ab = Segment(A, B)
    bc = Segment(B, C)
    b_ab = bisector(ab)
    b_bc = bisector(bc)
    center = b_ab * b_bc
    if center is None:
        return None
    radius = (abs(center - A) + abs(center - B) + abs(center - C)) / 3
    return Circle(center, radius)


class BoundingBox:
    """Axis-aligned bounding box (legacy/limited use)."""

    # TODO: obsolete

    def __init__(self, g=None):
        if g is None:
            self.bottom_left = 0
            self.top_right = 0
        elif isinstance(g, CircularArc):
            angles = [0, math.pi / 2, math.pi, math.pi * 3 / 2]
            points = []
            points.append(g(g.theta1))
            points.append(g(g.theta2))
            for beta in angles:
                if is_angle_between(g.theta1, beta, g.theta2):
                    points.append(g(beta))

            self.bottom_left = min(p.real for p in points) + 1J * min(p.imag for p in points)
            self.top_right = max(p.real for p in points) + 1J * max(p.imag for p in points)
        elif isinstance(g, Circle):
            self.bottom_left = g.center - g.radius - 1J * g.radius
            self.top_right = g.center + g.radius + 1J * g.radius
        elif isinstance(g, Segment):
            self.bottom_left = min(g.A.real, g.B.real) + 1J * min(g.A.imag, g.B.imag)
            self.top_right = max(g.A.real, g.B.real) + 1J * max(g.A.imag, g.B.imag)
        elif isinstance(g, Line):
            # TODO: except if parallel to real or imaginary axis
            self.bottom_left = 0
            self.top_right = 0  # should be inf
        else:
            print("ERROR")
            raise ValueError()

    def make_square(self):
        """Expand to the larger side to make the box square (centered)."""
        size_x = self.top_right.real - self.bottom_left.real
        size_y = self.top_right.imag - self.bottom_left.imag
        size = max(size_x, size_y)
        self.bottom_left -= (size - size_x) / 2 + 1J * (size - size_y) / 2
        self.top_right += (size - size_x) / 2 + 1J * (size - size_y) / 2

    def add_padding(self, units=None, fraction=None):
        """Add absolute (`units`) or proportional (`fraction`) padding to the box."""
        if units is None and fraction is None:
            raise ValueError("no padding")
        if units is not None:
            self.bottom_left -= units + 1J * units
            self.top_right += units + 1J * units
        if fraction is not None:
            padding = (self.top_right - self.bottom_left) * fraction
            self.bottom_left -= padding
            self.top_right += padding

    def __repr__(self):
        return f"Bounding box from bottom left: {self.bottom_left} to top right{self.top_right}))"

    def __ior__(self, other):
        """Join two bounding boxes (in-place union)."""
        self.bottom_left = min(self.bottom_left.real, other.bottom_left.real) + 1J * min(
            self.bottom_left.imag, other.bottom_left.imag
        )
        self.top_right = max(self.top_right.real, other.top_right.real) + 1J * max(
            self.top_right.imag, other.top_right.imag
        )
        return self


def translate(element, displacement):
    """
    Translate a geometric element by a complex displacement.

    Supports: `Segment`, `Line`, `Circle`, `PolySegment`, `CircularArc`,
    `OrientedCircularArc`, scalars (`complex`/`int`/`float`), and `None`.
    """
    if type(element) is Segment:
        return Segment(element.A + displacement, element.B + displacement)
    if type(element) is Line:
        return Line(element.A + displacement, element.B + displacement)
    if type(element) is Circle:
        return Circle(element.center + displacement, element.radius)
    if type(element) is PolySegment:
        return PolySegment([p + displacement for p in element.points])
    if type(element) is CircularArc:
        return CircularArc(element.center + displacement, element.radius, element.theta1, element.theta2)
    if type(element) is OrientedCircularArc:
        return OrientedCircularArc(
            element.center + displacement, element.radius, element.theta1, element.theta2, element.reversed
        )
    if type(element) is complex or type(element) is int or type(element) is float:
        return element + displacement
    if element is None:
        return None
    raise TypeError(f"Translation is not defined for {type(element)}")


def bounding_box(g):
    """
    Axis-aligned bounding box for a geometry or iterable of geometries.

    Returns:
        (min_complex, max_complex)
    """
    if isinstance(g, CircularArc):
        min_x, max_x = min(g.A.real, g.B.real), max(g.A.real, g.B.real)
        min_y, max_y = min(g.A.imag, g.B.imag), max(g.A.imag, g.B.imag)
        for angle in [0, math.pi / 2, math.pi, math.pi * 3 / 2]:
            if is_angle_between(g.theta1, angle, g.theta2):
                p = g(angle)
                min_x, max_x = min(min_x, p.real), max(max_x, p.real)
                min_y, max_y = min(min_y, p.imag), max(max_y, p.imag)
        return complex(min_x, min_y), complex(max_x, max_y)
    if isinstance(g, Segment):
        return complex(min(g.A.real, g.B.real), min(g.A.imag, g.B.imag)), complex(
            max(g.A.real, g.B.real), max(g.A.imag, g.B.imag)
        )
    elif isinstance(g, Circle):
        return g.center - (1 + 1j) * g.radius, g.center + (1 + 1j) * g.radius
    elif g is None:
        return 0, 0
    elif isinstance(g, complex):
        return complex(g), complex(g)
    else:
        bb = [bounding_box(_) for _ in g]
        return complex(min(_.real for _, __ in bb), min(_.imag for _, __ in bb)), complex(
            max(__.real for _, __ in bb), max(__.imag for _, __ in bb)
        )


def angle_between(z1, z2, z3):
    """
    Return the absolute angle at `z2` between vectors (`z1 - z2`) and (`z3 - z2`) in radians.
    """
    v1 = z1 - z2
    v2 = z3 - z2
    angle_rad = cmath.phase(v2 / v1)
    return abs(angle_rad)