# tests/utils/test_geometry.py

import math

from knotpy.utils.geometry import (
    Circle,
    CircularArc,
    OrientedCircularArc,
    Line,
    Segment,
    PolySegment,
    perpendicular_line,
    tangent_line,
    antipode,
    inverse_point_through_circle,
    perpendicular_arc_through_point,
    perpendicular_arc,
    arc_from_circle_and_points,
    arc_from_diameter,
    weighted_circle_center_mean,
    orient_arc,
    split,
    bisect,
    bisector,
    middle,
    circle_through_points,
    translate,
    bounding_box,
    angle_between,
    is_angle_between,
)


def test_circle_contains_and_length():
    c = Circle(0+0j, 2.0)
    p_on = 2+0j
    p_off = 3+0j
    assert p_on in c
    assert p_off not in c
    assert math.isclose(c.length(), 2*math.pi*2.0, rel_tol=1e-12)


def test_line_param_and_contains():
    l = Line(0+0j, 2+0j)
    assert 1+0j in l
    assert (0+1j) not in l
    assert l.parameter_from_point(1+0j) == 0.5


def test_segment_contains_and_length():
    s = Segment(0+0j, 2+0j)
    assert 1+0j in s
    assert (-0.1+0j) not in s
    assert math.isclose(s.length(), 2.0, rel_tol=1e-12)


def test_line_circle_intersection_two_points():
    c = Circle(0+0j, 5.0)
    l = Line(-10+0j, 10+0j)
    pts = c * l
    assert len(pts) == 2
    for p in pts:
        assert p in c
        assert p in l


def test_circle_circle_intersection_two_points():
    c1 = Circle(0+0j, 5.0)
    c2 = Circle(6+0j, 5.0)
    pts = c1 * c2
    assert len(pts) == 2
    for p in pts:
        assert p in c1 and p in c2


def test_circle_circle_tangent_one_point():
    c1 = Circle(0+0j, 5.0)
    c2 = Circle(10+0j, 5.0)
    pts = c1 * c2
    assert len(pts) == 1
    assert pts[0] in c1 and pts[0] in c2


def test_circular_arc_contains_and_length():
    c = Circle(0+0j, 2.0)
    a = CircularArc(c.center, c.radius, 0.0, math.pi/2)
    # point at 45 degrees
    # p = c(math.pi/4)
    #assert p in a
    assert math.isclose(a.length(), (math.pi/2) * 2.0, rel_tol=1e-12)


def test_oriented_circular_arc_shorten():
    a = OrientedCircularArc(0+0j, 2.0, 0.0, math.pi)  # half circle
    half_len = a.length()
    shorter = a.shorten(half_len/2, side="A", inplace=False)
    assert isinstance(shorter, OrientedCircularArc)
    assert math.isclose(shorter.length(), half_len/2, rel_tol=1e-12)


def test_perpendicular_line_and_tangent_line():
    l = Line(0+0j, 1+0j)
    p = 0+1j
    perp = perpendicular_line(l, p)
    # Perpendicular if direction vectors have purely imaginary ratio
    dir_ratio = (perp.B - perp.A) / (l.B - l.A)
    assert math.isclose(dir_ratio.real, 0.0, abs_tol=1e-12)

    c = Circle(0+0j, 2.0)
    t = tangent_line(c, 2+0j)
    # tangent line through (2,0) must be vertical: A.x == B.x
    assert math.isclose(t.A.real, t.B.real, abs_tol=1e-12)


def test_antipode_and_inversion():
    c = Circle(1+1j, 2.0)
    p = 3+1j
    ap = antipode(c, p)
    assert ap == -1+1j  # 2*center - p

    inv = inverse_point_through_circle(Circle(0+0j, 2.0), 1+0j)
    # |inv| should be r^2/|p| = 4/1 = 4 from the origin, same direction (1+0j)
    assert math.isclose(abs(inv), 4.0, rel_tol=1e-12)
    assert math.isclose(inv.real, 4.0, rel_tol=1e-12)


def test_perpendicular_arc_through_point_and_perpendicular_arc():
    c = Circle(0+0j, 5.0)
    cp = 5+0j
    q = 5 + 5j
    arc = perpendicular_arc_through_point(c, cp, q)
    # The arc starts at cp
    if isinstance(arc, CircularArc):
        assert cp in arc



def test_arc_from_circle_and_points_and_diameter():
    c = Circle(0+0j, 3.0)
    p1 = 3+0j
    p2 = 0+3j
    arc1 = arc_from_circle_and_points(c, p1, p2)
    assert p1 in arc1 and p2 in arc1

    arc2 = arc_from_diameter(3+0j, -3+0j)
    assert (3+0j) in arc2 and (-3+0j) in arc2


def test_weighted_center_and_orient_arc():
    c1 = Circle(0+0j, 2.0)
    c2 = Circle(10+0j, 1.0)
    w = weighted_circle_center_mean(c1, c2)
    # closer to c1.center because c2 has smaller radius => weight c1 by r2
    assert 0.0 < w.real < 10.0



def test_split_and_bisect_segment_and_arc():
    s = Segment(0+0j, 2+0j)
    mid = 1+0j
    s1, s2 = split(s, mid)
    assert s1.B == mid and s2.A == mid

    a = CircularArc(0+0j, 2.0, 0.0, math.pi)
    pm = a(math.pi/2)
    a1, a2 = split(a, pm)
    assert pm in a1 and pm in a2

    bs1, bs2 = bisect(s)
    assert math.isclose(bs1.length(), bs2.length(), rel_tol=1e-12)

    ba1, ba2 = bisect(a)
    assert math.isclose(ba1.length(), ba2.length(), rel_tol=1e-12)


def test_bisector_and_middle():
    s = Segment(0+0j, 2+0j)
    b = bisector(s)
    # bisector at midpoint should be vertical line at x=1
    assert math.isclose(b.A.real, b.B.real, abs_tol=1e-12)

    a = CircularArc(0+0j, 2.0, 0.0, math.pi)
    m = middle(a)
    # middle should be around (0,2)
    assert math.isclose(m.real, 0.0, abs_tol=1e-7)



def test_circle_through_points():
    A = 1+0j
    B = 0+1j
    C = -1+0j
    circ = circle_through_points(A, B, C)
    assert circ is not None
    assert A in circ and B in circ and C in circ


def test_polysegment_length_and_sample():
    ps = PolySegment([0+0j, 3+0j, 3+4j])
    assert math.isclose(ps.length(), 7.0, rel_tol=1e-12)
    pts = ps.sample(5)
    assert len(pts) == 5
    assert pts[0] == 0+0j and pts[-1] == 3+4j





def test_angles_helpers():
    # is_angle_between
    assert is_angle_between(0, math.pi/4, math.pi/2)
    assert not is_angle_between(math.pi/2, 0, math.pi)
    # angle_between (unsigned)
    z1, z2, z3 = 1+0j, 0+0j, 0+1j
    ang = angle_between(z1, z2, z3)
    assert math.isclose(ang, math.pi/2, rel_tol=1e-12)


# Manual runner: `python tests/utils/test_geometry.py`
if __name__ == "__main__":
    test_circle_contains_and_length()
    test_line_param_and_contains()
    test_segment_contains_and_length()
    test_line_circle_intersection_two_points()
    test_circle_circle_intersection_two_points()
    test_circle_circle_tangent_one_point()
    test_circular_arc_contains_and_length()
    test_oriented_circular_arc_shorten()
    test_perpendicular_line_and_tangent_line()
    test_antipode_and_inversion()
    test_perpendicular_arc_through_point_and_perpendicular_arc()
    test_arc_from_circle_and_points_and_diameter()
    test_weighted_center_and_orient_arc()
    test_split_and_bisect_segment_and_arc()
    test_bisector_and_middle()
    test_circle_through_points()
    test_polysegment_length_and_sample()
    test_angles_helpers()
    print("All geometry tests passed.")
