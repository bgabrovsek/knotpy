
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.notation.native import to_knotpy_notation, from_knotpy_notation

def test_native_notation_to_from():

    k = PlanarDiagram()
    k.add_vertices_from("ab")
    k.add_crossings_from("cd")
    k.set_arcs_from("a0b0,a1c0,a2d3,b1d2,b2c1,c2d1,c3d0")
    k.name = "my diagram"
    k.nodes["a"].attr = {"color": 3}
    k.nodes["b"].attr = {"color": 7}
    k.nodes["a"][0].attr = {"color": 8}
    k.nodes["a"][1].attr = {"color": 9}
    k.nodes["d"][3].attr = {"color": 10}
    k.framing=3

    notation = to_knotpy_notation(k)
    k_parsed = from_knotpy_notation(notation)

    assert k == k_parsed

def test_native_notation_from():

    notation_a = "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 d1 d0) d=X(c3 c2 b1 a2)"
    notation_b = "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 d1 d0) d=X(c3 c2 b1 a2) "
    notation_c = "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 d1 d0) d=X(c3 c2 b1 a2) ['name'='my diagram','framing'=3]"
    notation_d = "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 d1 d0) d=X(c3 c2 b1 a2) ['name'='my diagram','framing'=3; a:{'color'=3} b:{'color'=7}]"
    notation_e = "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 d1 d0) d=X(c3 c2 b1 a2) ['name'='my diagram','framing'=3; a:{'color'=3} b:{'color'=7}; b0:{'color'=8} c0:{'color'=9} a2:{'color'=10}]"

    k_a = from_knotpy_notation(notation_a)  # no attributes
    k_b = from_knotpy_notation(notation_b)  # with spaces
    k_c = from_knotpy_notation(notation_c)  # with diagram attributes
    k_d = from_knotpy_notation(notation_d)  # with node attributes
    k_e = from_knotpy_notation(notation_e)  # with

    k = PlanarDiagram()
    k.add_vertices_from("ab")
    k.add_crossings_from("cd")
    k.set_arcs_from("a0b0,a1c0,a2d3,b1d2,b2c1,c2d1,c3d0")

    assert k == k_a
    assert k == k_b
    assert not k == k_c
    assert not k == k_d
    assert not k == k_e

    k.name = "my diagram"
    k.framing=3

    assert not k == k_a
    assert not k == k_b
    assert k == k_c
    assert not k == k_d
    assert not k == k_e

    k.nodes["a"].attr = {"color": 3}
    k.nodes["b"].attr = {"color": 7}

    assert not k == k_a
    assert not k == k_b
    assert not k == k_c
    assert k == k_d
    assert not k == k_e

    k.nodes["a"][0].attr = {"color": 8}
    k.nodes["a"][1].attr = {"color": 9}
    k.nodes["d"][3].attr = {"color": 10}

    assert not k == k_a
    assert not k == k_b
    assert not k == k_c
    assert not k == k_d
    assert k == k_e


def test_native_notation_to():

    notation_a = "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 d1 d0) d=X(c3 c2 b1 a2)"
    notation_c = "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 d1 d0) d=X(c3 c2 b1 a2) ['name'='my diagram','framing'=3]"
    notation_d = "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 d1 d0) d=X(c3 c2 b1 a2) ['name'='my diagram','framing'=3; a:{'color'=3} b:{'color'=7}]"
    notation_e = "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 d1 d0) d=X(c3 c2 b1 a2) ['name'='my diagram','framing'=3; a:{'color'=3} b:{'color'=7}; b0:{'color'=8} c0:{'color'=9} a2:{'color'=10}]"

    k = PlanarDiagram()
    k.add_vertices_from("ab")
    k.add_crossings_from("cd")
    k.set_arcs_from("a0b0,a1c0,a2d3,b1d2,b2c1,c2d1,c3d0")

    assert to_knotpy_notation(k) == notation_a

    k.name = "my diagram"
    k.framing=3

    assert to_knotpy_notation(k) == notation_c

    k.nodes["a"].attr = {"color": 3}
    k.nodes["b"].attr = {"color": 7}

    assert to_knotpy_notation(k) == notation_d

    k.nodes["a"][0].attr = {"color": 8}
    k.nodes["a"][1].attr = {"color": 9}
    k.nodes["d"][3].attr = {"color": 10}


    notation_e_ = to_knotpy_notation(k)

    notation_e = notation_e.split("[")
    notation_e_ = notation_e_.split("[")
    assert notation_e[0] == notation_e_[0]

    assert set(notation_e[1].replace("]","").split(" ")) == set(notation_e_[1].replace("]","").split(" "))


if __name__ == "__main__":
    test_native_notation_to_from()
    test_native_notation_from()
    test_native_notation_to()