# tests/test_planardiagram_basic.py

import pytest

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram, planar_diagram_from_data
from knotpy.classes.endpoint import Endpoint
from knotpy.classes.node import Vertex, Crossing


def make_simple_diagram():
    """Helper: two vertices with one arc between them."""
    d = PlanarDiagram()
    d.add_vertices_from(["a", "b"])
    d.set_arc((("a", 0), ("b", 0)))
    return d


def test_add_vertices_and_arcs():
    d = make_simple_diagram()

    assert d.number_of_nodes == 2
    # Each endpoint appears once; one arc = 2 endpoints
    assert d.number_of_endpoints == 2
    assert d.number_of_arcs == 1

    # Twin checks
    ep_a0 = ("a", 0)
    ep_b0 = ("b", 0)
    assert isinstance(d.twin(ep_a0), Endpoint)
    assert d.twin(ep_a0).node == "b"
    assert d.twin(ep_b0).node == "a"


def test_copy_shallow_and_attr_independence():
    d = make_simple_diagram()
    d.attr["name"] = "original"
    d.attr["framing"] = 2

    c = d.copy()
    assert isinstance(c, PlanarDiagram)
    assert c is not d
    assert c == d  # structural equality using your comparator
    assert c.attr is not d.attr  # separate dicts
    assert c.attr["name"] == "original"
    assert c.attr["framing"] == 2

    c.attr["name"] = "changed"
    assert d.attr["name"] == "original"  # independence


def test_remove_arc_and_endpoints():
    d = make_simple_diagram()
    assert d.number_of_arcs == 1

    d.remove_arc((("a", 0), ("b", 0)))
    assert d.number_of_arcs == 0
    # Endpoints removed from both nodes
    assert d.number_of_endpoints == 0


def test_relabel_nodes_updates_endpoints():
    d = make_simple_diagram()
    d.relabel_nodes({"a": "x"})

    # Node keys changed
    assert "x" in d.nodes and "a" not in d.nodes

    # Endpoints updated
    # New arc is between ("x", 0) and ("b", 0)
    ep_x0 = ("x", 0)
    t = d.twin(ep_x0)
    assert t.node == "b"
    assert d.number_of_arcs == 1


def test_compare_ordering_by_size_and_degree():
    a = make_simple_diagram()
    b = make_simple_diagram()
    assert a == b

    # Add an extra isolated vertex to b; b > a by node count
    b.add_vertex("c")
    assert a < b
    assert not (a > b)


def test_orientation_constraints_in_oriented_diagram():
    d = OrientedPlanarDiagram()
    d.add_vertices_from(["p", "q"])
    # In an oriented diagram, trying to create a plain Endpoint should error
    with pytest.raises(ValueError):
        d.set_endpoint(("p", 0), ("q", 0))  # default create_using=Endpoint (unoriented)


def test_planar_diagram_from_data_with_instance():
    # Build a source diagram
    src = PlanarDiagram()
    src.attr["name"] = "src"
    src.add_vertices_from(["u", "v"])
    src.set_arc((("u", 0), ("v", 0)))

    # Build a new diagram from the source instance
    dst = planar_diagram_from_data(incoming_data=src, create_using=PlanarDiagram)

    assert isinstance(dst, PlanarDiagram)
    assert dst is not src
    assert dst == src
    # Attributes are copied
    assert dst.attr["name"] == "src"


def test_add_crossings_from_and_degree_sequence():
    d = PlanarDiagram()
    d.add_crossings_from(["c1", "c2"], color="red")

    assert d.number_of_crossings == 2
    # Crossings should be degree-4 nodes
    assert all(len(d._nodes[c]) == 4 for c in d.crossings)
    # Attributes set
    assert all(d._nodes[c].attr.get("color") == "red" for c in d.crossings)
