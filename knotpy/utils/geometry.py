"""
Library for (numerical) geometry.
"""
import math
import cmath


__all__ = ["Circle", "CircularArc", "Line", "Segment", "BoundingBox",
           "antipode", "perpendicular_line", "perpendicular_arc", "bisect", "tangent_line", "middle", "bisector",
           "is_angle_between", "perpendicular_arc_through_point", "circle_through_points"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'


DIAMETER_ERROR = 0.0001  # error for a point that is still considered that lies on the circle
MIN_SEGMENT_SIZE = 1E-8  # what distance do we still consider to be a segment?
MIN_DETERMINANT = 1E-8  # what distance do we still consider to be a segment?
CIRCLE_DISTANCE_ERROR = 1E-6 # distance for determining tangent/disjoint/intersectant circles
#ERROR = 1e-8  # distance between points to be considered the same (e.g. for determining midpoints of circles)


class Circle:

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def __contains__(self, point):
        """Does the point lie on the circle?"""
        #print(abs(abs(point - self.center) - self.radius))
        return abs(abs(point - self.center) - self.radius) <= DIAMETER_ERROR

    def __mul__(self, other):
        """Intersection between geometric objects."""


        if isinstance(other, Circle):
            return _intersection_circle_circle(self, other)

        if isinstance(other, Line):
            return _intersection_circle_line(self, other)

        raise TypeError(f"Intersection of a circle and {type(other)} not supported")

    def length(self):
        return 2 * math.pi * self.radius  # 2pi*r

    def __call__(self, angle1, angle2=None):
        """The point line at angle or the circular arc if two angles are give."""
        if angle2 is not None:
            return CircularArc(self.center, self.radius, angle1, angle2)
        raise NotImplementedError()

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

    def length(self):
        diff_angle = ((self.theta2 % (2 * math.pi)) - (self.theta1 % (2 * math.pi))) % (2 * math.pi)
        return diff_angle * self.radius  # arc length is angle * radius

    def __call__(self, angle1, angle2=None):
        """The point line at angle or the circular arc if two angles are give."""
        if angle2 is not None:
            return CircularArc(self.center, self.radius, angle1, angle2)

        if is_angle_between(self.theta1, angle1, self.theta2) or is_angle_between(self.theta2, angle1, self.theta1):
            return self.center + self.radius * math.cos(angle1) + 1j * self.radius * math.sin(angle1)
        else:
            raise ValueError(f"The angle {angle1} does not lie on the circular arc {self}")

    def __str__(self):
        return f"Circular arc at {self.center:.5f} with radius {self.radius:.5f} and angles {self.theta1:.5f} and {self.theta2:.5f}"


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

    def __call__(self, t):
        """The point on the line A + t * directional vector."""
        return self.A + t * (self.B - self.A) if 0 <= t <= 1 else None

    def __str__(self):
        return f"Segment through points {self.A:.5f} and {self.B:.5f}"



##### BOUNDING BOX ####

def bounding_box(a):
    if isinstance(a, CircularArc):
        pass

    if isinstance(a, Circle):
        pass

    if isinstance(a, Segment):
        pass

    if isinstance(a, Line):
        pass

    if isinstance(a, complex):
        pass

    raise TypeError("Parameter is not a geometric object or point.")


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


def perpendicular_arc(circle, circle1, circle2, order=None):
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
    :return: circle on which the arcs lie in, angles of the circles such that the arc is the part of the circle from
     the 1st angle and the 2nd angle (angles are in radians)
    """
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
            order += [2, 1]
        else:
            order += [1, 2]

        return inv_arc
    else:
        # if the arc is the diameter, return a line
        order += [1, 2]
        return Segment(point1, point2)


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

def middle(g):
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

if __name__ == '__main__':

    print("test")

    c = CircularArc(0.039+0.726j, 0.687, 0.003, 0.76)
    s = Segment(0.976+1.103j, 0.473+0.9j)
    p = c * s
    print(p)

    exit()
    print("Tests")
    c = Circle(2+1j, 3)
    a = CircularArc(2+1j, 3, 0, math.pi/4)
    l = Line(3+4j, 4+2j)
    s = Segment(3+4j, 4+2j)
    print(f"{c}\n{a}\n{l}\n{s}\n")

    print("circle-circle")

    print("Point on circle", 5+1j in c, 5+1j in Circle(7+1j, 2))
    print("Point on circle", 5+1j in c, 5+1j in Circle(7+1j, 2))
    print("Circle-circle 0", Circle(5-2j, 1) * c)  # []
    print("Circle-circle 1", Circle(7+1j, 2) * c)  # [5+1j]
    print("Circle-circle 2", Circle(-1-3j, math.sqrt(5)) * c)  # [-0.35-0.86j, 0.87-1.78j]

    print("\nline-line")

    print("Point on line", 1+8j in l)
    print("Point not on line", 1+7j in l)
    print("Line-line 0", Line(4+5j,3+7j) * l)
    print("Line-line 1", Line(1+6j, 5+5j) * l)  # 2.142 + 5.714j

    print("\nsegment-segment")
    print("Point on segment", 1.3 -8.3j in Segment(1-8j,2-9j))
    print("Point not on segment", 1.3 -8.4j in Segment(1-8j,2-9j))
    print("Segment-segment 0", Segment(1-8j,2-9j) * Segment(2-11j,3-7j))
    print("Segment-segment 1", Segment(1-8j,2-9j) * Segment(1-11j,2-7j)) #  (1.6-8.6j)

    print("\nline-segment")
    print("Line-segment 0", Segment(1-8j,2-9j) * Line(2-11j,3-7j))  # None
    print("Line-segment 1", Line(1-8j,2-9j) * Segment(2-11j,3-7j))  # (2.4-9.4j)

    print("\ncircle-line")
    print("Circle-line 0", l * c)  # # [3.1+3.789j, 4.894+0.211j]
    print("Circle-line 1", c * Line(-1,-1+4j)) # [-1+1j]
    print("Circle-line 2", Circle(7+1j, 2) * l)

    print("\ncircle-segment")
    print("Circle-segment 0", Segment(2-10j, 3-8j) * c)
    print("Circle-segment 1", Segment(2+4j, 3+4j) * c)  # [2+4j] (tangent)
    print("Circle-segment 1", Segment(0+4j, 3+4j) * c)  # [2+4j] (tangent)
    print("Circle-segment 1", s * c)  # [3.1+3.789j]
    print("Circle-segment 2", Segment(-2+2j,12+10j) * c)  # [-0.22+3.02j, 1.39+3.94j]

    print("\nperpendicular arc")
    print(perpendicular_arc(Circle(2+1j,3), Circle(6+1j,1), Circle(2+6j,2)))
    print(perpendicular_arc(Circle(2+1j,3), Circle(6+1j,1), Circle(-3+1j,2)))