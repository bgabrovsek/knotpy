"""
Library for (numerical) geometry.
"""
import math
import cmath

__all__ = ["Circle", "CircularArc", "Line", "Segment", "BoundingBox", "PolySegment",
           "antipode", "perpendicular_line", "bisect", "tangent_line", "middle", "bisector",
           "is_angle_between", "perpendicular_arc_through_point", "perpendicular_arc",  "circle_through_points",
           "weighted_circle_center_mean", "split"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

DIAMETER_ERROR = 0.0001  # error for a point that is still considered that lies on the circle
MIN_SEGMENT_SIZE = 1E-8  # what distance do we still consider to be a segment?
MIN_DETERMINANT = 1E-8  # what distance do we still consider to be a segment?
CIRCLE_DISTANCE_ERROR = 1E-6 # distance for determining tangent/disjoint/intersectant circles
#ERROR = 1e-8  # distance between points to be considered the same (e.g. for determining midpoints of circles)

class Circle:
    """
    Representation of a geometric circle in the complex plane.

    Attributes:
        center (Any): The center of the circle, typically represented as a complex number or
            a coordinate pair (depending on the context of usage).
        radius (float): The radius of the circle, defining its size and extent.
    """

    def __init__(self, center: complex, radius: float):
        """
        Represents a circle characterized by a center point and a radius.

        Attributes:
            center: A complex number representing the circle's center.
            radius: A float representing the radius of the circle.
        """
        self.center = center
        self.radius = radius

    def __contains__(self, point: complex) -> bool:
        """
        Check whether a given point lies on the circle.

        Args:
            point: Complex coordinate representing the point to be checked.

        Returns:
            bool: True if the point lies on the circle, False otherwise.
        """
        return abs(abs(point - self.center) - self.radius) <= DIAMETER_ERROR

    def __mul__(self, other):
        """
        Compute the intersection between the circle and another geometric object.

        Args:
            other (Circle | Line): The geometric object to intersect with.

        Returns:
            Resultant geometric objects representing the intersection. The return type
            and structure depend on the intersection method and the input types.

        Raises:
            TypeError: If the type of other is not Circle or Line.
        """

        if isinstance(other, Circle):
            return _intersection_circle_circle(self, other)

        if isinstance(other, Line):
            return _intersection_circle_line(self, other)

        raise TypeError(f"Intersection of a circle and {type(other)} not supported")

    # def antipodal(self, point: complex) -> complex:
    #     """
    #     Return the antipodal point (reflection of the given point) through the center of the circle.
    #
    #     Args:
    #         point (complex): The point to be reflected through the  circle's center.
    #
    #     Returns:
    #         complex: The reflected point (antipodal point).
    #     """
    #     return 2 * self.center - point

    def length(self):
        """Return the circumference of the circle."""
        return 2 * math.pi * self.radius  # 2pi*r

    def __call__(self, angle1, angle2):
        """
        Return the circular atc between two angles, lying on the circle.

        Args:
            angle1: The starting angle (in radians).
            angle2: Optional; The second angle (in degrees).

        Returns:
            CircularArc: An object representing the arc defined by the center, radius, and the angles.

        Raises:
            NotImplementedError: If the second angle (angle2) is not provided.
        """
        return CircularArc(self.center, self.radius, angle1, angle2)

    def __str__(self):
        return f"Circle at {self.center:.5f} with radius {self.radius:.5f}"

class CircularArc(Circle):

    def __init__(self, center, radius, theta1, theta2):
        self.theta1 = theta1 % (2 * math.pi)
        self.theta2 = theta2 % (2 * math.pi)
        super().__init__(center, radius)

    def __contains__(self, point):
        """Does the point lie on the circular arc?"""
        if not super().__contains__(point):
            return False
        # is the angle on the arc?
        return is_angle_between(self.theta1, cmath.phase(point - self.center), self.theta2)

    def angle(self):
        return ((self.theta2 % (2 * math.pi)) - (self.theta1 % (2 * math.pi))) % (2 * math.pi)

    def length(self):
        return self.angle() * self.radius  # arc length is angle * radius

    def __call__(self, angle1, angle2=None):
        """The point line at angle or the circular arc if two angles are give."""
        if angle2 is not None:
            return CircularArc(self.center, self.radius, angle1, angle2)

        if is_angle_between(self.theta1, angle1, self.theta2) or is_angle_between(self.theta2, angle1, self.theta1):
            return self.center + self.radius * math.cos(angle1) + 1j * self.radius * math.sin(angle1)
        else:
            raise ValueError(f"The angle {angle1} does not lie on the circular arc {self}")

    def __neg__(self):
        return CircularArc(self.center, self.radius, self.theta2, self.theta1)

    @property
    def A(self):
        return self(self.theta1)
    @property
    def B(self):
        return self(self.theta2)

    def __str__(self):
        return f"Circular arc at {self.center:.5f} with radius {self.radius:.5f} and angles {self.theta1:.5f} and {self.theta2:.5f}"

class OrientedCircularArc(CircularArc):

    def __init__(self, center, radius, theta1, theta2, reversed=False):
        self.reversed = reversed
        super().__init__(center, radius, theta1, theta2)

    def set_orientation(self, start_point, end_point):
        """
        Set the orientation so that the point at angle theta1 is closer to start_point and point at angle theta2 is closer to end_point.
        """
        point1 = self.center + self.radius * math.cos(self.theta1) + 1j * self.radius * math.sin(self.theta1)
        point2 = self.center + self.radius * math.cos(self.theta2) + 1j * self.radius * math.sin(self.theta2)

        if end_point is None:
            self.reversed = abs(point1 - start_point) > abs(point2 - start_point)
        elif start_point is None:
            self.reversed = abs(point1 - end_point) < abs(point2 - end_point)
        elif end_point is not None and start_point is not None:
            self.reversed = abs(point1 - end_point) + abs(point2 - start_point) > abs(point1 - start_point) + abs(point2 - end_point)
        else:
            raise ValueError("start_point and/or end_point must be specified")

    def shorten(self, length, side, inplace=False):
        """ Shorten arc from side 'A' (start) or 'B' (end). """
        if self.length() <= length:
            return None
        if side not in ['A', 'B']:
            raise ValueError(f"side must be 'A' or 'B', not {side}")

        #print("delta angle", round((self.theta2 - self.theta1) * (180 / math.pi)) )

        delta = ((self.theta2 - self.theta1) % (2 * math.pi)) * length / self.length()  # maybe mode 2*pi?

        #print("reversed", reversed, side, round(self.theta1 * (180 / math.pi)), round(self.theta2 * (180 / math.pi)), round(delta * (180 / math.pi)), )

        if self.reversed == (side == 'A'):
            if inplace:
                self.theta2 = (self.theta2 - delta) % (2 * math.pi)
            else:
                return OrientedCircularArc(self.center, self.radius, self.theta1, (self.theta2 - delta) % (2 * math.pi), reversed=self.reversed)
        else:
            if inplace:
                self.theta1 = self.theta1 + delta
            else:
                return OrientedCircularArc(self.center, self.radius, self.theta1 + delta, self.theta2, reversed=self.reversed)

    # def __call__(self, angle1, angle2=None):
    #     """The point line at angle or the circular arc if two angles are give."""
    #     if angle2 is not None:
    #         return OrientedCircularArc(self.center, self.radius, angle1, angle2, reversed=self.reversed)
    #
    #     if is_angle_between(self.theta1, angle1, self.theta2) or is_angle_between(self.theta2, angle1, self.theta1):
    #         if self.reversed:
    #             pass
    #         else:
    #             return self.center + self.radius * math.cos(angle1) + 1j * self.radius * math.sin(angle1)
    #     else:
    #         raise ValueError(f"The angle {angle1} does not lie on the circular arc {self}")

    # def __neg__(self):
    #     return OrientedCircularArc(self.center, self.radius, self.theta2, self.theta1, reversed=not self.reversed)

    @property
    def A(self):
        return self(self.theta2) if self.reversed else self(self.theta1)
    @property
    def B(self):
        return self(self.theta1) if self.reversed else self(self.theta2)

    def __str__(self):
        return f"Oriented Circular arc at {self.center:.5f} with radius {self.radius:.5f} and angles {self.theta1:.5f} and {self.theta2:.5f}" + (" reversed" if self.reversed else "")

class Line:
    def __init__(self, A, B):
        self.A = A
        self.B = B
        if abs(self.B - self.A) < MIN_SEGMENT_SIZE:
            raise ValueError(f"Points {A} and {B} too close to each other.")

    def __contains__(self, point):
        """Does the point lie on the line?
        The point lies on the line through A and B if the complex number point-A is a (real) multiple of
        the complex number B-A.
        """
        return self.parameter_from_point(point) is not None
        #t = (point - self.A) / (self.B - self.A)  # Calculate the scalar multiple factor
        #return abs(t.imag) <= DIAMETER_ERROR

    def __mul__(self, other):
        """Intersection between geometric objects."""
        if isinstance(other, Circle):
            return _intersection_circle_line(other, self)

        if isinstance(other, Line):
            return _intersection_line_line(self, other)

    def parameter_from_point(self, point):
        """ For the line T = A + t(B-A) get the parameter t so that T = point."""
        t = (point - self.A) / (self.B - self.A)
        #print(t, abs(t.imag), DIAMETER_ERROR)
        if abs(t.imag) > DIAMETER_ERROR:
            return None  # point does not lie on the line
        return t.real

    def __neg__(self):
        return Line(self.B, self.A)

    @staticmethod
    def length(self):
        return float("inf")

    def __call__(self, t):
        """The point on the line A + t * directional vector."""
        return self.A + t * (self.B - self.A)

    def __str__(self):
        return f"Line through points {self.A:.5f} and {self.B:.5f}"

class Segment(Line):

    def __contains__(self, point):
        """Does the point lie on the line segment?
        The point lies on the line through A and B if the complex number point-A is a (real) multiple of
        the complex number B-A and the quotient is between 0 and 1.
        """
        t = (point - self.A) / (self.B - self.A)  # Calculate the scalar multiple factor
        return abs(t.imag) <= DIAMETER_ERROR and 0 <= t.real <= 1

    def length(self):
        return abs(self.B - self.A)  # |B-A|

    def set_orientation(self, start_point, end_point):
        """
        Set the orientation so that the point A is closer to start_point and point B closer to end_point.
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
        """Shorten by length on the side indicated by side ('A' or 'B')."""
        if self.length() <= length:
            return None
        s = (self.B - self.A) / abs(self.B - self.A)  # Normalize the direction
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
        """The point on the line A + t * directional vector. if both t1 and t2 are given, return the segment from t1 to t2."""
        if t2 is None:
            return self.A + t1 * (self.B - self.A) if 0 <= t1 <= 1 else None
        else:
            if 0 <= t1 <= 1 and 0 <= t2 <= 1:
                return Segment(self(t1), self(t2))
            else:
                return None

    def sample(self, n):
        """Split a segment into n evenly spaced complex points from A to B (inclusive)."""

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
        """Return the total length of the piecewise linear curve."""
        return sum(abs(self.points[i + 1] - self.points[i]) for i in range(len(self.points) - 1))

    def sample(self, n):
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

##### BOUNDING BOX ####

# def bounding_box(a):
#     if isinstance(a, CircularArc):
#         pass
#
#     if isinstance(a, Circle):
#         pass
#
#     if isinstance(a, Segment):
#         pass
#
#     if isinstance(a, Line):
#         pass
#
#     if isinstance(a, complex):
#         pass
#
#     raise TypeError("Parameter is not a geometric object or point.")

##### INTERSECTION #####

def _intersection_circle_circle(a: Circle, b: Circle):
    """Find the intersection points of two circles on the complex plane.
     Let d be the distance between the centers of circle 1 and 2.
     Let point1 and point2 be the intersection points.
     Let 2m be the distance between point1 and point2 (circle segment length).
     Let h be the distance between h be the distance between the center of circle 1 and the midpoint of point 1
     and point2. Then the following to Pythagorean theorems hold: h^2 + m^2 = r1^2 and (d-h)^2 + m^2 = r2^2"""

    dist = abs(a.center - b.center)  # distance between centers

    if dist >= a.radius + b.radius + CIRCLE_DISTANCE_ERROR:
        """Disjoint circles"""
        solutions = []  # no solution

    elif abs(dist - b.radius - a.radius) <= CIRCLE_DISTANCE_ERROR:
        """Tangent circles"""
        solutions = [(b.center * a.radius + a.center * b.radius) / (b.radius + a.radius)]  # one solution

    else:
        """Circles intersect in two points"""
        h = (dist ** 2 + b.radius ** 2 - a.radius ** 2) / (2 * dist)
        m = math.sqrt(b.radius ** 2 - h ** 2)  # half the distance between the two intersections
        v = _normalize(a.center - b.center)  # normalized vector from z1 to z2
        h = h * v  # vector from z1 to z2 of length h
        m = m * (1j * v)  # vector perpendicular to the vector from z1 to z2
        solutions = [b.center + h + m, b.center + h - m]  # two intersections

    # next check is mostly needed for circular arcs
    return [point for point in solutions if point in a and point in b]  # overhead if point lies on a circle

def _intersection_line_line(a: Line, b: Line):
    """Compute intersection of two Lines.
        Return: intersection point or None
       Description:
       The line through points a1 and a2 has an equation T = a1 + t * (a2 - a1),
       the line through points b1 and b2 has an equation T' = b1 + t' * (b2 - b1), thus we are solving the system
       a1 + t * (a2 - a1) = b1 + t' * (b2 - b1) using Cramer's rule. """
    det = _complex_determinant(a.B - a.A, b.A - b.B)
    if abs(det) < MIN_DETERMINANT:  # are lines parallel?
        return None
    else:
        t = _complex_determinant(b.A - a.A, b.A - b.B) / det
        # t_ = _complex_determinant(a.B - a.A, b.A - a.A) / det  # could check a(t) == b(t_)
        point = a(t)
        if point is None:
            return None
        #print(a)
        #print(b)
        #print(point in a, point in b)
        return point if point is None or (point in a and point in b) else None

def _intersection_circle_line(c: Circle, l: Line):
    """ Compute intersection between a circle and a line (segment).
    :param c: Circle
    :param l:
    :return:
    TODO: tangent line
    """

    s = l.B - l.A  # directional vector parallel to the line
    n = s * 1j  # vector perpendicular to the line
    # diameter points perpendicular to the segment
    e1 = c.center + c.radius * n / abs(n)
    e2 = c.center - c.radius * n / abs(n)
    # point in the middle of the circle segment of the line on which the segment lies on
    p = _intersection_line_line(Line(l.A, l.B), Segment(e1, e2))  # midpoint of the two intersections
    #print("lin", p)
    if p is None:
        return []
    d = abs(p - c.center)  # distance between midpoint and center
    m = math.sqrt(c.radius * c.radius - d * d)  # 1/2 length od the circle segment

    result = [p + m * s / abs(s), p - m * s / abs(s)] if m != 0 else [p]
    return [point for point in result if point in c and point in l]

##### OTHER FUNCTIONS #####

def _normalize(z: complex) -> complex:
    """normalize the number z, return z/|z|."""
    return z / abs(z)

def _complex_determinant(z: complex, w: complex):
    """Compute the expression z.real * w.imag - z.imag * w.real"""
    return (z.conjugate() * w).imag

def is_angle_between(theta1: float, theta2: float, theta3: float) -> bool:
    """Check if angle theta2 is between angles theta1 and theta3 (modulo 2*pi).
    :param theta1: First angle in radians.
    :param theta2: Angle to be checked in radians.
    :param theta3: Third angle in radians.
    :return: True if theta2 is between theta1 and theta3, False otherwise.
    """
    # Normalize angles to be in the range [0, 2*pi)
    theta1 = theta1 % (2 * math.pi)
    theta2 = theta2 % (2 * math.pi)
    theta3 = theta3 % (2 * math.pi)

    # Check if theta2 is between theta1 and theta3 (modulo 2*pi)
    if theta1 <= theta3:
        return theta1 <= theta2 <= theta3
    else:
        return theta1 <= theta2 or theta2 <= theta3

#### GEOMETRIC OPERATIONS
def perpendicular_line(l: Line, p: complex):
    """Return a line that is perpendicular to the other line. and goes through point p"""
    return Line(p, p + 1j * (l.B - l.A))

def tangent_line(c: Circle, p: complex):
    """Return tangent line assuming point lies on circle, otherwise returns line perpendicular to the radius through
    the center and p."""
    return perpendicular_line(Line(c.center, p), p)

def antipode(circle, point):
    # TODO: this is a duplicate of the class method
    return circle.center - (point - circle.center)

def inverse_point_through_circle(circle, point):
    """Perform inverse geometry transformation on a given point with respect to a circle.

    :param circle:  tuple representing the circle (center as a complex number, radius)
    :param point: the complex number representing the point to be inversed.
    :return: inversed point as a complex number

    Description:
    Given a point P(x, y), a circle with center C(cx, cy), and radius r,
    this function calculates the inverse geometry transformation of the point with respect to the circle.
    The inverse point P'(x', y') is determined such that OP * OP' = r^2, where OP is the distance from
    the center C to the original point P and OP' is the distance from the center C to the inverse point P'.

    #Example:
    #>>> inverse_point_through_circle((3+4j, 5), 0+0j)
    #(13.4+14.5j)

    """
    d = abs(circle.center-point)
    return circle.center + (circle.radius**2 / d**2) * (point - circle.center)

def perpendicular_arc_through_point(circle, circle_point, point):
    """Return the arc that is:
    - perpendicular to the circle at circle_point
    - starts at the circle point and goes through the point
    - (if the point lies on the circle, the arc is perpendicular also at point."""

    # print("peep")
    # print(circle, circle_point, point)

    tangent = tangent_line(circle, circle_point)
    segment = Segment(circle_point, point)
    seg_bis = bisector(segment)
    center = tangent * seg_bis  # intersection
    #print(">>>", tangent, seg_bis, center)
    if center is None:  # no intersection
        return Segment(circle_point, point)
    theta1 = cmath.phase(circle_point - center) % (2*math.pi)
    theta2 = cmath.phase(point - center)
    angle_diff = (theta2 - theta1) % (2 * math.pi)
    if angle_diff > math.pi:
        theta1, theta2 = theta2, theta1

    arc = CircularArc(center, abs(center - circle_point), theta1, theta2)
    #print("ARC", arc)
    #print(arc)
    return arc

def perpendicular_arc(circle, circle1, circle2):
    # TODO: use perpendicular_arc_through _points
    """Return the perpendicular circular arc through the circle that starts and ends at the intersection of circle and
    circle1 and circle2, respectively.
    Circles are given as pairs (complex number representing the center, radius)

    The conditions of the circular arc are thus:
      - the center z of the circle (z,r),
      - the intersection i0 of circles (z,r) and (z0,r0),
      - the intersection i1 of circles (z,r) and (z1,r1),
    with the extra condition that the arc is perpendicular to all circles (z,r), (z0,r0), and (z1,r1).

    :param circle: the main circle through which the arc is placed
    :param circle1: the 1st circle tangent to circle
    :param circle2: the 2nd circle tangent to circle
    :param order: returns order of circles 1,2 in the arc (if the arcs starts at circle1, order is [1,2], else [2,1]
    :param approx: the circle do not need to touch or overlap, but the closest possible such point will be assumed
    :return: circle on which the arcs lie in, angles of the circles such that the arc is the part of the circle from
     the 1st angle and the 2nd angle (angles are in radians)
    """
    order = []
    approx = False
    if order is None:
        order = []
    else:
        order.clear()

    # exact intersection
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
    """
    Create a circular arc connecting i1 and i2, which is perpendicular to circle. We obtain such an arc/circle
    by inverting the midpoint through the circle. By construction, the new point is the center of the perpendicular
    circle.
    """

    # TODO: what if midpoint is in the center?
    if abs(midpoint - circle.center) > MIN_SEGMENT_SIZE:
        inv_midpoint = inverse_point_through_circle(circle, midpoint)  # the arc li
        inv_arc = CircularArc(inv_midpoint,
                              abs(inv_midpoint - point1),
                              cmath.phase(point1 - inv_midpoint),  # the angle of the point i1 on the inversed circle
                              cmath.phase(point2 - inv_midpoint)  # the angle of the point i1 on the inversed circle
                              )

        if (inv_arc.theta2 - inv_arc.theta1) % (2 * math.pi) > math.pi:  # make the arc the smaller of the two
            inv_arc.theta1, inv_arc.theta2 = inv_arc.theta2, inv_arc.theta1

        return inv_arc
    else:
        # if the arc is the diameter, return a line
        return Segment(point1, point2)

def arc_from_circle_and_points(circle, point1, point2):
    """Return the circular arcs lying on circle going from point1 to point2."""
    if point1 not in circle and point2 not in circle:
        raise ValueError("The points to not lie on the circle")

    return CircularArc(circle.center, abs(circle.center - point1), cmath.phase(point1 - circle.center), cmath.phase(point2 - circle.center))

def arc_from_diameter(point1, point2):
    """Return the circular arcs lying on circle going from point1 to point2."""
    return arc_from_circle_and_points(Circle((point1 + point2) / 2, abs(point1 - point2) / 2), point1, point2)

def weighted_circle_center_mean(circle1:Circle, circle2:Circle):
    """ Compute a weighted mean, so that the intersection of cicles are scaled proportinately so they meet."""
    radii = circle1.radius + circle2.radius
    return circle1.center * (circle2.radius / radii) + circle2.center * (circle1.radius / radii)

#
# def perpendicular_arc2(circle, circle1, circle2):
#     # TODO: use perpendicular_arc_through _points
#     """Return the perpendicular circular arc through the circle that starts and ends at the intersection of circle and
#     circle1 and circle2, respectively.
#     Circles are given as pairs (complex number representing the center, radius)
#
#     The conditions of the circular arc are thus:
#       - the center z of the circle (z,r),
#       - the intersection i0 of circles (z,r) and (z0,r0),
#       - the intersection i1 of circles (z,r) and (z1,r1),
#     with the extra condition that the arc is perpendicular to all circles (z,r), (z0,r0), and (z1,r1).
#
#     :param circle: the main circle through which the arc is placed
#     :param circle1: the 1st circle tangent to circle
#     :param circle2: the 2nd circle tangent to circle
#     """
#
#
#     # if approx:
#     #     # approximate intersections
#     #     point1 = [weighted_circle_center_mean(circle, circle1)]
#     #     point2 = [weighted_circle_center_mean(circle, circle2)]
#     # else:
#     #     # exact intersections
#     #     point1 = circle * circle1
#     #     point2 = circle * circle2
#
#     point1 = circle * circle1
#     point2 = circle * circle2
#
#     if len(point1) == 0 or len(point2) == 0:
#         raise ValueError("No intersection point computing perpendicular arc")
#     if len(point1) == 2 or len(point2) == 2:
#         raise ValueError("two intersection points of tangent circles")
#
#     point1 = point1[0]
#     point2 = point2[0]
#     midpoint = 0.5 * (point1 + point2)
#     """
#     Create a circular arc connecting i1 and i2, which is perpendicular to circle. We obtain such an arc/circle
#     by inverting the midpoint through the circle. By construction, the new point is the center of the perpendicular
#     circle.
#     """
#
#
#     # TODO: what if midpoint is in the center?
#     if abs(midpoint - circle.center) > MIN_SEGMENT_SIZE:
#         inv_midpoint = inverse_point_through_circle(circle, midpoint)  # the arc li
#         inv_arc = CircularArc(inv_midpoint,
#                               abs(inv_midpoint - point1),
#                               cmath.phase(point1 - inv_midpoint),  # the angle of the point i1 on the inversed circle
#                               cmath.phase(point2 - inv_midpoint)  # the angle of the point i1 on the inversed circle
#                               )
#         #
#         # if (inv_arc.theta2 - inv_arc.theta1) % (2 * math.pi) > math.pi:  # make the arc the smaller of the two
#         #     inv_arc.theta1, inv_arc.theta2 = inv_arc.theta2, inv_arc.theta1
#         #     order += [2, 1]
#         # else:
#         #     order += [1, 2]
#
#         return inv_arc
#     else:
#         # if the arc is the diameter, return a line
#         return Segment(point1, point2)
#

def orient_arc(g: CircularArc | Segment, start_point=None, end_point=None):
    """ From an unoriented arc/segment, return an oriented one so that the (starting) point 'A' is on average closer to
    start_point and the (ending) point 'B' is on average closer to end_point."""
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
    """Split arc/segment g at point (that lies on the arc/segment)"""
    if isinstance(g, Segment):
        return Segment(g.A, point), Segment(point, g.B)

    if isinstance(g, CircularArc):
        angle = cmath.phase(point - g.center)
        return CircularArc(g.center, g.radius, g.theta1, angle), CircularArc(g.center, g.radius, angle, g.theta2)

    raise TypeError("Can only split an arc or a segment.")

def bisect(g):
    """Split object (Segment or CircularArc) into two equal halves."""

    if isinstance(g, Segment):
        return Segment(g.A, 0.5 * (g.A + g.B)), Segment(0.5 * (g.A + g.B), g.B)

    if isinstance(g, CircularArc):
        angle = 0.5 * (g.theta1 + g.theta2)
        if abs(g.theta1 - angle) % (2 * math.pi) > math.pi/2 and abs(g.theta1 - angle) % (2 * math.pi) > math.pi/2:
            angle = angle + math.pi

        return (CircularArc(g.center, g.radius, g.theta1, angle),
                CircularArc(g.center, g.radius, angle, g.theta2))

    raise TypeError("Can only bisect an arc or a segment.")

def bisector(s: Segment) -> Line:
    """Return the bisector line of the segment"""
    return perpendicular_line(s, 0.5 * (s.A + s.B))

def middle(g) -> complex:
    """Returns geometric center of a segment or arc"""
    if isinstance(g, Segment):
        return 0.5 * (g.A + g.B)

    if isinstance(g, CircularArc):
        # TODO: does this work for all angles?
        angle = 0.5 * (g.theta1 + g.theta2)
        if abs(g.theta1 - angle) % (2 * math.pi) > math.pi/2 and abs(g.theta1 - angle) % (2 * math.pi) > math.pi/2:
            return g(angle + math.pi)
        else:
            return g(angle)

    if isinstance(g, complex):
        return g

    raise TypeError("Can only bisect an arc or a segment.")

def circle_through_points(A, B, C):
    """Return a circle through points A, B, and C."""
    ab = Segment(A, B)
    bc = Segment(B, C)
    b_ab = bisector(ab)
    b_bc = bisector(bc)
    center = b_ab * b_bc
    if center is None:
        return None
    radius = (abs(center - A) + abs(center - B) + abs(center - C))/3
    return Circle(center, radius)

class BoundingBox:
    # TODO: obsolete

    def __init__(self, g=None):

        #print("bb")

        if g is None:
            self.bottom_left = 0  # bottom left
            self.top_right = 0  # top right
        elif isinstance(g, CircularArc):
            angles = [0, math.pi / 2, math.pi, math.pi * 3 / 2]
            points = list()  # extreme points
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
            # todo: except if parallel to real or imaginary axis
            self.bottom_left = 0
            self.top_right = 0  # should be inf
        else:
            print("ERROR")
            raise ValueError()
        #print(self)

    def make_square(self):
        size_x = self.top_right.real - self.bottom_left.real
        size_y = self.top_right.imag - self.bottom_left.imag
        size = max(size_x, size_y)
        self.bottom_left -= (size - size_x)/2 + 1J * (size - size_y)/2
        self.top_right += (size - size_x)/2 + 1J * (size - size_y)/2

        """
        bl = -3 + 1
        tr = 4 + 11
        sizex = 7
        sizey = 10
        size= 10
        bl -= (10-7)/2 
        
        """

    def add_padding(self, units=None, fraction=None):
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
        """join two bounding boxes"""
        self.bottom_left = min(self.bottom_left.real, other.bottom_left.real) + 1J * min(self.bottom_left.imag, other.bottom_left.imag)
        self.top_right = max(self.top_right.real, other.top_right.real) + 1J * max(self.top_right.imag, other.top_right.imag)
        return self

def translate(element, displacement):
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
        return OrientedCircularArc(element.center + displacement, element.radius, element.theta1, element.theta2, element.reversed)
    if type(element) is complex or type(element) is int or type(element) is float:
        return element + displacement
    if element is None:
        return None
    raise TypeError(f"Translation is not defined for {type(element)}")

def bounding_box(g):
    # TODO: also consider angles 0, 90, 180, 270 for arcs

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
        return complex(min(g.A.real, g.B.real), min(g.A.imag, g.B.imag)), complex(max(g.A.real, g.B.real), max(g.A.imag, g.B.imag))
    elif isinstance(g, Circle):
        return g.center - (1 + 1j) * g.radius, g.center + (1 + 1j) * g.radius
    elif g is None:
        return 0, 0
    elif isinstance(g, complex):
        return complex(g), complex(g)
    else:
        bb = [bounding_box(_) for _ in g]
        return complex(min(_.real for _, __ in bb), min(_.imag for _, __ in bb)), complex(max(__.real for _, __ in bb), max(__.imag for _, __ in bb))

def angle_between(z1, z2, z3):
    v1 = z1 - z2
    v2 = z3 - z2
    angle_rad = cmath.phase(v2 / v1)
    return abs(angle_rad)  # in radians