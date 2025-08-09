# knotpy/algorithms/closure.py
"""
Closure of an open knot (knotoid).

Provides underpass, overpass, and double-sided (over+under) closures by routing a path
through faces in the dual planar diagram.
"""

from __future__ import annotations

__all__ = ["closure"]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek"

from collections import deque

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.duality import dual_planar_diagram
from knotpy.algorithms.remove import remove_bivalent_vertex
from knotpy.algorithms.naming import unique_new_node_name


def _bfs_shortest_path(graph: PlanarDiagram, start, goal):
    """
    Find the shortest path in a graph using the Breadth-First Search (BFS) algorithm.

    This function explores paths in a graph layer by layer starting from the `start` node to
    find the shortest possible path to the `goal` node. The function returns the shortest
    path if one exists. If no path exists between `start` and `goal`, the function returns None.

    Args:
        graph (PlanarDiagram): The graph structure to search, where nodes and connections are
            defined as per the PlanarDiagram class or equivalent structure.
        start: The starting node for the search.
        goal: The target node to find the shortest path to.

    Returns:
        list: A list representing the nodes in the shortest path from `start` to `goal`,
            including both endpoints. If no path exists, returns None.
    """
    # Queue for exploring nodes and tracking paths
    queue = deque([[start]])
    visited = set()

    while queue:
        # Get the current path and node
        path = queue.popleft()
        node = path[-1]

        # Check if the goal is reached
        if node == goal:
            return path  # This is the shortest path

        # If the node hasn't been visited yet, explore its neighbors
        if node not in visited:
            visited.add(node)
            for neighbor in graph.nodes[node]:
                new_path = list(path)
                new_path.append(neighbor.node)
                queue.append(new_path)

    return None  # Return None if no path exists between start and goal


def _face_intersection_arc(k: PlanarDiagram, f, g):
    """Return the oriented arc shared by consecutive faces ``f`` and ``g``.

    If face ``f`` contains arc ``(A, B)``, face ``g`` should contain ``(B, A)``.
    The returned pair is oriented so that the first endpoint is CCW with respect to ``f``.
    """
    for i in range(len(f)):
        f_pair = (f[i], f[(i + 1) % len(f)])
        for j in range(len(g)):
            g_pair = (g[j], g[(j + 1) % len(g)])
            if (
                f_pair[0].node == g_pair[1].node
                and f_pair[1].node == g_pair[0].node
                and (f_pair[1].position + 1) % k.degree(f_pair[1].node) == g_pair[0].position
            ):
                return f_pair[1], g_pair[1]
    return None


def _underpass_closure(k: PlanarDiagram, A, B, arcs):
    """Perform an underpass closure from leaf ``A`` to leaf ``B`` along ``arcs``."""
    k = k.copy()
    previous_open_endpoint = (A, 1)
    for ep_f, ep_g in arcs:
        crossing = unique_new_node_name(k)
        k.add_crossing(crossing_for_adding=crossing)
        k.set_arc((previous_open_endpoint, (crossing, 0)))
        k.set_arc((ep_f, (crossing, 3)))
        k.set_arc((ep_g, (crossing, 1)))
        previous_open_endpoint = (crossing, 2)
    k.set_arc((previous_open_endpoint, (B, 1)))

    if k.degree(A) != 2 or k.degree(B) != 2:
        raise ValueError("The leaves should have degree 2 after underpass closure.")
    remove_bivalent_vertex(k, A)
    remove_bivalent_vertex(k, B)
    return k


def _overpass_closure(k: PlanarDiagram, A, B, arcs):
    """Perform an overpass closure from leaf ``A`` to leaf ``B`` along ``arcs``."""
    k = k.copy()
    previous_open_endpoint = (A, 1)
    for ep_f, ep_g in arcs:
        crossing = unique_new_node_name(k)
        k.add_crossing(crossing_for_adding=crossing)
        k.set_arc((previous_open_endpoint, (crossing, 1)))
        k.set_arc((ep_f, (crossing, 0)))
        k.set_arc((ep_g, (crossing, 2)))
        previous_open_endpoint = (crossing, 3)
    k.set_arc((previous_open_endpoint, (B, 1)))

    if k.degree(A) != 2 or k.degree(B) != 2:
        raise ValueError("The leaves should have degree 2 after overpass closure.")
    remove_bivalent_vertex(k, A)
    remove_bivalent_vertex(k, B)
    return k


def _over_and_under_closure(k: PlanarDiagram, A, B, arcs):
    """Perform a double-sided closure: one overpass and one underpass from ``A`` to ``B``."""
    k = k.copy()
    previous_open_endpoint_over = (A, 1)
    previous_open_endpoint_under = (A, 2)
    for ep_f, ep_g in arcs:
        crossing_over = unique_new_node_name(k)
        k.add_crossing(crossing_for_adding=crossing_over)
        crossing_under = unique_new_node_name(k)
        k.add_crossing(crossing_for_adding=crossing_under)

        k.set_arc((previous_open_endpoint_over, (crossing_over, 1)))
        k.set_arc((previous_open_endpoint_under, (crossing_under, 0)))

        k.set_arc((ep_g, (crossing_over, 2)))
        k.set_arc((ep_f, (crossing_under, 3)))
        k.set_arc(((crossing_over, 0), (crossing_under, 1)))

        previous_open_endpoint_over = (crossing_over, 3)
        previous_open_endpoint_under = (crossing_under, 2)

    k.set_arc((previous_open_endpoint_over, (B, 2)))
    k.set_arc((previous_open_endpoint_under, (B, 1)))

    if k.degree(A) != 3 or k.degree(B) != 3:
        raise ValueError("The leaves should have degree 3 after double-sided closure.")
    return k


def closure(k: PlanarDiagram, over: bool = False, under: bool = False) -> PlanarDiagram:
    """Close a knotoid by routing through the dual graph between its two degree-1 vertices.

    You must choose at least one of ``over`` or ``under``. If both are True, a double-sided
    closure is performed (one overpass and one underpass).

    Args:
        k: Planar diagram with exactly two leaves (degree-1 vertices).
        over: Use overpass closure.
        under: Use underpass closure.

    Returns:
        A new ``PlanarDiagram`` with the chosen closure applied.

    Raises:
        ValueError: If neither over nor under is selected.
        ValueError: If the diagram does not have exactly two leaves.
    """
    if not under and not over:
        raise ValueError("Select at least one closure type: over=True or under=True.")

    leafs = [v for v in k.vertices if k.degree(v) == 1]
    if len(leafs) != 2:
        raise ValueError("Can only close a diagram with exactly two leaves.")
    A, B = leafs

    dual = dual_planar_diagram(k)

    A_ep = k.endpoint_from_pair((A, 0))
    B_ep = k.endpoint_from_pair((B, 0))
    A_face = next(f for f in dual.vertices if A_ep in f)
    B_face = next(f for f in dual.vertices if B_ep in f)

    path = _bfs_shortest_path(dual, A_face, B_face)
    arcs = [_face_intersection_arc(k, f, g) for f, g in zip(path, path[1:])]

    if over and under:
        return _over_and_under_closure(k, A, B, arcs)
    if over:
        return _overpass_closure(k, A, B, arcs)
    return _underpass_closure(k, A, B, arcs)


if __name__ == "__main__":
    pass