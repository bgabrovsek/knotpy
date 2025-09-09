"""
Invisible support primitives for drawing.

This module augments a diagram with temporary, hidden structure so
circle-packing (or other layout methods) can draw it robustly. We never change
the topology of the input diagram; instead we add auxiliary nodes/arcs marked
with the attribute ``_support=True`` so the renderer can route around bridges,
cut-vertices, etc.

Notes
-----
- Support nodes/arcs are **invisible** to the end user: anything with
  ``attr['_support'] is True`` should be treated as hidden while drawing.
"""

from __future__ import annotations

import warnings

from knotpy.algorithms.insert import insert_endpoint, insert_arc
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.topology import bridges, leafs, kinks, loops
from knotpy.algorithms.cut_set import cut_nodes
from knotpy.algorithms.subdivide import subdivide_endpoint
from knotpy.notation.native import to_knotpy_notation

__all__ = ["non_leaf_bridges", "_add_support_arcs", "drawable"]
__version__ = "0.2"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"


def non_leaf_bridges(k: PlanarDiagram) -> list:
    """Return bridges that are not incident to leaves.

    Args:
        k: Planar diagram.

    Return:
        list: Bridges (as frozensets of two endpoints) whose endpoints are not at
        degree-1 vertices.
    """
    return [b for b in bridges(k) if all(k.degree(ep.node) > 1 for ep in b)]


def _visible(__obj) -> bool:
    """Check if a diagram object should be shown (i.e., is not a support helper).

    Args:
        __obj: Node/endpoint-like object with an ``attr`` mapping.

    Return:
        bool: False iff ``__obj.attr['_support']`` is True; True otherwise.
    """
    if not hasattr(__obj, "attr"):
        return True
    #print(__obj, not (__obj.attr.get("_support", False)))
    return not (__obj.attr.get("_support", False))


def _subdivide_two_adjacent_arcs(k: PlanarDiagram, endpoint) -> tuple:
    """Subdivide the two arcs adjacent to an endpoint and mark helpers as support.

    For an endpoint (node, position), split the counter-clockwise and clockwise
    adjacent arcs by inserting bivalent vertices. The new vertices are marked
    with ``_support=True``.

    Args:
        k: Planar diagram.
        endpoint: Tuple ``(node, position)`` identifying the base endpoint.

    Return:
        tuple: ``(node_left, node_right, left_ep, right_ep)`` where
        ``node_left``/``node_right`` are the new bivalent vertices and
        ``left_ep``/``right_ep`` are their ``(node, 0)`` endpoints.
    """
    node, pos = endpoint
    degree = k.degree(node)
    left_endpoint = k.endpoint_from_pair((node, (pos - 1) % degree))
    right_endpoint = k.endpoint_from_pair((node, (pos + 1) % degree))

    node_left = subdivide_endpoint(k, left_endpoint)
    node_right = subdivide_endpoint(k, right_endpoint)
    k.nodes[node_left].attr["_support"] = True
    k.nodes[node_right].attr["_support"] = True

    return node_left, node_right, k.endpoint_from_pair((node_left, 0)), k.endpoint_from_pair((node_right, 0))


def _add_support_arcs_for_cut_vertices(k: PlanarDiagram) -> None:
    """Add invisible support arcs around cut-vertices (excluding leaf/kink adjacencies).

    Repeatedly:
      1) Identify cut-vertices not adjacent to leaves and not themselves kink crossings.
      2) Subdivide each incident arc by a bivalent vertex (marked ``_support=True``).
      3) Stitch consecutive bivalent vertices with a tiny arc on both directions to
         keep the local embedding connected for packing.

    Args:
        k: Planar diagram (modified in place).
    """

    def _cut_nodes_not_leaf_adjacent_or_kink():
        cn = cut_nodes(k)
        leaf_adj = [k.twin((l, 0)).node for l in leafs(k)]
        kink_crossings = [ep.node for ep in kinks(k)]
        return set(cn) - set(leaf_adj) - set(kink_crossings)

    while nodes := _cut_nodes_not_leaf_adjacent_or_kink():
        node = nodes.pop()
        degree = k.degree(node)
        bivertices = [subdivide_endpoint(k, (node, pos)) for pos in range(degree)]

        for v in bivertices:
            k.nodes[v].attr["_support"] = True

        for i in range(degree):
            adj_vert_a, adj_vert_b = bivertices[i], bivertices[(i + 1) % degree]
            adj_pos_a = k.degree(adj_vert_a)
            adj_pos_b = 1
            insert_endpoint(
                k,
                target_endpoint=(adj_vert_a, adj_pos_a),
                adjacent_endpoint=(adj_vert_b, adj_pos_b),
                _support=True,
            )
            insert_endpoint(
                k,
                target_endpoint=(adj_vert_b, adj_pos_b),
                adjacent_endpoint=(adj_vert_a, adj_pos_a),
                _support=True,
            )


def _long_bridges(k: PlanarDiagram):
    """Merge bridges chained through a degree-2 vertex into a single “long” bridge.

    Args:
        k: Planar diagram.

    Return:
        set | list: Set (or empty list) of bridges, where each element is a
        frozenset of the two “outer” endpoints after collapsing degree-2 joints.
    """
    _bridges = non_leaf_bridges(k)
    if not _bridges:
        return []

    while bivertices := [v for ep1, ep2 in _bridges for v in [ep1.node, ep2.node] if k.degree(v) == 2]:
        v = bivertices[0]
        endpoints = []
        for b in _bridges:
            ep1, ep2 = b
            if ep1.node == v or ep2.node == v:
                endpoints.append([ep1, ep2, b] if ep2.node == v else [ep2, ep1, b])
        if len(endpoints) != 2:
            raise ValueError(f"bivalent bridges error, endpoints: {endpoints}")
        _bridges.remove(endpoints[0][2])
        _bridges.remove(endpoints[1][2])
        _bridges.add(frozenset([endpoints[0][0], endpoints[1][0]]))

    return _bridges


def _add_support_arcs_for_bridges(k: PlanarDiagram) -> None:
    """Add invisible parallel/adjacent arcs along bridges so layout can route strands.

    For each (possibly long) bridge:
      * If both endpoints are leaves, connect the two leaf neighborhoods with a
        pair of small parallel arcs.
      * Otherwise, create two “parallel” helper arcs on each side of the bridge
        by subdividing the adjacent positions and marking the helper vertices
        as ``_support=True``.

    Args:
        k: Planar diagram (modified in place).

    Raises:
        NotImplementedError: If a degree-2 vertex is encountered on an endpoint.
    """
    while all_bridges := _long_bridges(k):
        bridge = all_bridges.pop()

        endpoint_a, endpoint_b = bridge
        node_a, pos_a = endpoint_a
        node_b, pos_b = endpoint_b
        deg_a = k.degree(node_a)
        deg_b = k.degree(node_b)
        if deg_a == 2 or deg_b == 2:
            raise NotImplementedError("Support arcs for degree-2 vertices not supported")

        # Segment case (both endpoints are leaves)
        if deg_a == 1 and deg_b == 1:
            k.set_endpoint((node_a, 1), (node_b, 2), _support=True)
            k.set_endpoint((node_a, 2), (node_b, 1), _support=True)
            k.set_endpoint((node_b, 1), (node_a, 2), _support=True)
            k.set_endpoint((node_b, 2), (node_a, 1), _support=True)
            continue

        # Build helper endpoints around node_a
        if k.degree(node_a) == 1:
            node_a_right = node_a_left = node_a
            pos_a_right, pos_a_left = 1, 2
        else:
            node_a_right = subdivide_endpoint(k, (node_a, (pos_a + 1) % deg_a))
            node_a_left = subdivide_endpoint(k, (node_a, (pos_a - 1) % deg_a))
            pos_a_right = 1 if k.nodes[node_a_right][0].node == node_a else 2
            pos_a_left = 2 if k.nodes[node_a_right][0].node == node_a else 1
            k.nodes[node_a_right].attr["_support"] = True
            k.nodes[node_a_left].attr["_support"] = True

        # Build helper endpoints around node_b
        if k.degree(node_b) == 1:
            node_b_right = node_b_left = node_b
            pos_b_right, pos_b_left = 2, 1
        else:
            node_b_right = subdivide_endpoint(k, (node_b, (pos_b - 1) % deg_b))
            node_b_left = subdivide_endpoint(k, (node_b, (pos_b + 1) % deg_b))
            pos_b_right = 2 if k.nodes[node_b_right][0].node == node_b else 1
            pos_b_left = 1 if k.nodes[node_b_right][0].node == node_b else 2
            k.nodes[node_b_right].attr["_support"] = True
            k.nodes[node_b_left].attr["_support"] = True

        # Add the support arcs
        if k.degree(node_a) == 1:
            insert_arc(k, ((node_a_right, pos_a_right), (node_b_right, pos_b_right)), _support=True)
            insert_arc(k, ((node_a_left, pos_a_left), (node_b_left, pos_b_left)), _support=True)
        else:
            insert_arc(k, ((node_a_left, pos_a_left), (node_b_left, pos_b_left)), _support=True)
            insert_arc(k, ((node_a_right, pos_a_right), (node_b_right, pos_b_right)), _support=True)


def _add_support_arcs(k: PlanarDiagram):
    """Return a copy of the diagram with support arcs inserted.

    For every bridge, add two parallel arcs (or adjacent arcs at leaf endpoints).
    Then add local support around cut-vertices so circle-packing can embed the
    diagram without creating overlaps.

    Args:
        k: Planar diagram.

    Return:
        PlanarDiagram: A copy of ``k`` with invisible support elements added.

    Raises:
        ValueError: If bridges remain after bridge-support insertion.
    """
    k = k.copy()
    if k.name:
        name = k.name
        del k.attr["name"]
    else:
        name = None

    _add_support_arcs_for_bridges(k)

    if non_leaf_bridges(k):
        raise ValueError("Diagram has bridges after adding bridge-support arcs.")

    _add_support_arcs_for_cut_vertices(k)

    if name:
        k.name = name

    return k


def drawable(k: PlanarDiagram) -> tuple[bool, list]:
    """Check whether a diagram can be safely drawn without adding support.

    Args:
        k: Planar diagram.

    Return:
        tuple:
            - bool: False if the diagram contains non-leaf bridges, loops, or cut-nodes.
            - list[str]: Reasons detected (subset of ``{"bridge", "loop", "cut-node"}``).

    Side effects:
        Emits warnings describing the issues found (using concise native notation).
    """
    diagram_drawable = True
    error_text = []

    if non_leaf_bridges(k):
        warnings.warn(f"Diagram {to_knotpy_notation(k)} contains bridges (skipping)", UserWarning)
        error_text.append("bridge")
        diagram_drawable = False

    if loops(k):
        warnings.warn(f"Diagram {to_knotpy_notation(k)} contains loops (skipping)", UserWarning)
        error_text.append("loop")
        diagram_drawable = False

    if cut_nodes(k):
        warnings.warn(f"Diagram {to_knotpy_notation(k)} contains cut-nodes (skipping)", UserWarning)
        error_text.append("cut-node")
        diagram_drawable = False

    return diagram_drawable, error_text