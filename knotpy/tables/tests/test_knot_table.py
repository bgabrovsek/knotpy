from setuptools.command.build_py import assert_relative

from knotpy.tables.name import clean_name, parse_name, safe_clean_and_parse_name
import knotpy as kp

def test_clean_name():
    assert clean_name("3_1") == "3_1"
    assert clean_name("trefoil") == "3_1"
    assert clean_name("31") == "3_1"
    assert clean_name("112") == "11_2"
    assert clean_name("K10_14") == "10_14"
    assert clean_name("11a17") == "11a_17"
    assert clean_name("L6a2") == "L6a_2"
    assert clean_name("l6A2") == "L6a_2"
    assert clean_name("T31") == "T3_1"
    assert clean_name("H31") == "H3_1"
    assert clean_name("*3_1") == "3_1*"
    assert clean_name("3_1*") == "3_1*"
    assert clean_name("+3_1") == "3_1+"
    assert clean_name("-3_1") == "3_1-"
    assert clean_name("**k3_1") == "3_1"
    assert clean_name("-t3_1") == "T3_1-"
    assert clean_name("-*t3_1") == "T3_1*-"
    assert clean_name("*-t3_1") == "T3_1*-"
    assert clean_name("-t3_1*") == "T3_1*-"
    assert clean_name("*t3_1-") == "T3_1*-"
    assert clean_name("t3_1--*") == "T3_1*--"
    assert clean_name("3_1+-") == "3_1+-"
    assert clean_name("3_1{+-}") == "3_1+-"
    assert clean_name("3_1(+,-,+)") == "3_1+-+"
    assert clean_name(" L6a_2 {+,-,+,+,-} * ") == "L6a_2*+-++-"

def test_parse_name():
    # (type, crossing number, alt/nalt/None, index, mirror, orientation)
    assert parse_name("3_1") == ("knot", 3, None, 1, False, "")
    assert parse_name("11a_5") == ("knot", 11, "a", 5, False, "")
    assert parse_name("11n_7*") == ("knot", 11, "n", 7, True, "")
    assert parse_name("L6a_2") == ("link", 6, "a", 2, False, "")
    assert parse_name("L6n_3*+-") == ("link", 6, "n", 3, True, "+-")
    assert parse_name("T3_1++-") == ("theta", 3, None, 1, False, "++-")
    assert parse_name("H4_2*--++") == ("handcuff", 4, None, 2, True, "--++")
    assert parse_name("L6a_2*") == ("link", 6, "a", 2, True, "")
    assert parse_name("H0_1") == ("handcuff", 0, None, 1, False, "")
    assert parse_name("T0_1") == ("theta", 0, None, 1, False, "")


def test_knot_symmetry():


    k1 = kp.knot("9_32")
    k2 = kp.knot("9_32*")
    k3 = kp.knot("9_32+")
    k4 = kp.knot("9_32-")
    k5 = kp.knot("9_32*+")
    k6 = kp.knot("9_32*-")

    assert not k1.is_oriented()
    assert not k2.is_oriented()
    assert k3.is_oriented()
    assert k4.is_oriented()
    assert k5.is_oriented()
    assert k6.is_oriented()

    assert len({k1, k2, k3, k4, k5, k6}) == 6

    k1 = kp.knot("3_1")
    k2 = kp.knot("3_1*")
    assert k1 != k2

    k1 = kp.knot("3_1+")
    k2 = kp.knot("3_1-")
    k3 = kp.knot("3_1*+")
    k4 = kp.knot("3_1*-")

    assert k1 == k2
    assert k3 == k4
    assert k1 != k3
    assert k2 != k4


def test_knot_symmetry_count():


    # unoriented
    knots_a = kp.knots(range(10), oriented=False, mirror=False)
    knots_b = kp.knots(range(10), oriented=False, mirror=True)
    assert len(knots_a) == len(set(knots_a))
    assert len(knots_b) == len(set(knots_b))
    assert len({_.name for _ in knots_a}) == len(knots_a)  # all names disjoint
    assert len({_.name for _ in knots_b}) == len(knots_b)  # all names disjoint
    assert len(knots_a) < len(knots_b)

    # unoriented
    knots_c = kp.knots(range(10), oriented=True, mirror=False)
    knots_d = kp.knots(range(10), oriented=True, mirror=True)
    assert len(knots_c) == len(set(knots_c))
    assert len(knots_d) == len(set(knots_d))
    assert len({_.name for _ in knots_c}) == len(knots_c)  # all names disjoint
    assert len({_.name for _ in knots_d}) == len(knots_d)  # all names disjoint
    assert len(knots_c) < len(knots_d)
    assert len(knots_a) < len(knots_c)


def test_safe_parse_name():
    assert safe_clean_and_parse_name("3_1") is not None
    assert safe_clean_and_parse_name("3_1*") is not None
    assert safe_clean_and_parse_name("+3_1*") is not None
    assert safe_clean_and_parse_name("3_1110*-") is not None
    assert safe_clean_and_parse_name("77_1110*-+") is not None
    assert safe_clean_and_parse_name("31") is not None
    assert safe_clean_and_parse_name("98") is not None
    assert safe_clean_and_parse_name("987") is not None
    assert safe_clean_and_parse_name("9876") is None
    assert safe_clean_and_parse_name("9") is None
    assert safe_clean_and_parse_name(31) is not None
    assert safe_clean_and_parse_name(0) is None
    assert safe_clean_and_parse_name(3) is None
    assert safe_clean_and_parse_name(3100) is None
    assert safe_clean_and_parse_name(None) is None
    assert safe_clean_and_parse_name([1,2,3]) is None
    assert safe_clean_and_parse_name("") is None
    assert safe_clean_and_parse_name(lambda _: _) is None
    assert safe_clean_and_parse_name(range(3)) is None

def test_precomputed_homflypt():
    from knotpy.tables.knot import knot_precomputed_homflypt
    # unoriented
    for k in kp.knots(range(0, 7)):
        h1 = kp.homflypt(k, variables="xyz")
        h2 = knot_precomputed_homflypt(k)
        assert h2 is not None
        assert h1 == h2

    # unoriented + mirror
    for k in kp.knots(range(0, 7), mirror=True):
        h1 = kp.homflypt(k, variables="xyz")
        h2 = knot_precomputed_homflypt(k)
        assert h2 is not None
        assert h1 == h2

    # oriented + mirror
    for k in kp.knots(range(0, 8), mirror=True, oriented=True):
        h1 = kp.homflypt(k, variables="xyz")
        h2 = knot_precomputed_homflypt(k)
        assert h2 is not None
        assert h1 == h2

def test_identify():
    pd_code = "PD[X[1,9,2,8], X[3,10,4,11], X[5,3,6,2],X[7,1,8,12], X[9,4,10,5], X[11,7,12,6]]"
    k = kp.from_pd_notation(pd_code)
    assert kp.identify(k) == "6_2"
    assert kp.identify(kp.mirror(k)) == "6_2*"


    k = kp.orient(kp.from_pd_notation(kp.to_pd_notation(kp.knot("-9_32"))))
    ident = kp.identify(k)
    assert ident == "-9_32" or ident == "+9_32"

def test_same_polys():
    from collections import defaultdict
    groups = defaultdict(list)
    for k in kp.knots(range(1, 11), mirror=True):
        groups[kp.homflypt(k)].append(k.name)


    duplicate = {tuple(sorted(name)) for poly, name in groups.items() if len(name) > 1}
    assert duplicate == {('10_25*', '10_56*'), ('10_48', '10_48*'), ('10_103', '10_40'), ('10_103*', '10_40*'),
                         ('10_129*', '8_8'), ('10_132', '5_1*'), ('10_104', '10_104*'), ('10_156*', '8_16*'),
                         ('10_129', '8_8*'), ('10_25', '10_56'), ('10_125', '10_125*'), ('10_91', '10_91*'),
                         ('10_132*', '5_1'), ('9_42', '9_42*'), ('10_71', '10_71*'), ('10_156', '8_16')}

def test_unknot():
    k = kp.knot("unknot")
    assert kp.identify(k) == "0_1"

def test_unoriented():

    K = kp.knot("9_32")
    assert kp.identify(K) == "9_32"

    K = kp.mirror(K)
    assert kp.identify(K) == "9_32*"

def test_oriented():


    K = kp.knot("+9_32")
    assert kp.identify(K) == "+9_32"
    K1 = kp.reverse(K, inplace=False)
    assert kp.identify(K1) == "-9_32"
    K2 = kp.mirror(K, inplace=False)
    assert kp.identify(K2) == "+9_32*"
    K3 = kp.mirror(kp.reverse(K, inplace=False))
    assert kp.identify(K3) == "-9_32*"



    K = kp.knot("+9_32")
    K = kp.randomize_diagram(K, 1)
    assert kp.identify(K) == "+9_32" or kp.identify(K) == ['+9_32', '-9_32']

    K2 = kp.mirror(K, inplace=False)
    assert kp.identify(K2) == "+9_32*" or kp.identify(K2) == ['+9_32*', '-9_32*']

def test_symmetry_identification():

    assert kp.symmetry_type("3_1") == "reversible"
    assert kp.symmetry_type(kp.knot("3_1")) == "reversible"

    assert kp.symmetry_type("0_1") == "fully amphicheiral"
    assert kp.symmetry_type(kp.knot("0_1")) == "fully amphicheiral"

    k = kp.knot("culprit")
    assert kp.identify(k) == "0_1"

if __name__ == "__main__":

    print([k.name for k in kp.knots(range(11)) if kp.symmetry_type(k) == "chiral"])
    # Run test
    test_symmetry_identification()
    exit()
    test_oriented()
    test_unoriented()

    test_unknot()
    test_clean_name()
    test_parse_name()
    test_knot_symmetry()
    test_knot_symmetry_count()
    test_safe_parse_name()
    test_precomputed_homflypt()
    test_identify()
    test_same_polys()