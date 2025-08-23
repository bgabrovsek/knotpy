# knotpy/algorithms/canonical.py

"""
Putting a diagram into its canonical form.

Given a `PlanarDiagram`, this module computes a canonical representative by
relabeling nodes via a CCW BFS strategy from carefully chosen starting endpoints
(min-degree nodes with a minimal neighbor sequence). Disjoint components are
canonicalized independently and reassembled in canonical order.
"""

__all__ = ["canonical", "canonical_generator"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

from collections.abc import Iterable
from queue import Queue
from string import ascii_letters

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.node import Crossing
from knotpy.algorithms.degree_sequence import neighbour_sequence
from knotpy.algorithms.disjoint_union import number_of_disjoint_components, disjoint_union_decomposition, disjoint_union
from knotpy.algorithms.rewire import permute_node


def _under_endpoints_of_node(k: PlanarDiagram, node):
    """Endpoints to start from: under-endpoints for crossings; all for vertices."""
    if isinstance(k.nodes[node], Crossing):
        return [(node, 0), (node, 2)]
    return [(node, pos) for pos in range(k.degree(node))]


def _min_elements_by(items, key):
    """
    Return elements with minimal key value.

    Args:
        items: Iterable of items.
        key: Callable mapping item -> comparable value.

    Returns:
        list: Items whose key(item) is minimal.
    """
    items = list(items)
    if not items:
        return []
    keyed = [(item, key(item)) for item in items]
    m = min(v for _, v in keyed)
    return [item for item, v in keyed if v == m]


def _ccw_expand_node_names(k: PlanarDiagram, endpoint, node_names: list[str]):
    """
    Label nodes by CCW BFS starting from a given endpoint.

    Args:
        k: Planar diagram.
        endpoint: Tuple (node, position) to start from.
        node_names: Ordered list of new node names.

    Returns:
        tuple[dict, dict]: (node_relabel, node_first_position)
            node_relabel maps old node -> new name.
            node_first_position maps new name -> first position visited.
    """
    node_relabel: dict = {}  # keys are old node names, values ar enew node names
    node_first_position: dict = {}
    q = Queue()
    q.put(endpoint)

    while not q.empty():
        v, pos = q.get()

        if v not in node_relabel:
            new_name = node_names[len(node_relabel)]
            node_relabel[v] = new_name
            node_first_position[new_name] = pos
            deg = k.degree(v)
            # push CCW-ordered positions at v
            for rpos in range(1, deg):
                q.put((v, (pos + rpos) % deg))

        # traverse to adjacent endpoint
        adj_v, adj_pos = k.nodes[v][pos]
        if adj_v not in node_relabel:
            q.put((adj_v, adj_pos))

    return node_relabel, node_first_position


def canonical_generator(diagrams: Iterable[PlanarDiagram]):
    """Yield canonical forms for a stream of diagrams."""
    if not isinstance(diagrams, Iterable):
        raise TypeError("Input must be an iterable.")
    for d in diagrams:
        yield canonical(d)


def canonical(k: PlanarDiagram | set | list | tuple | Iterable[PlanarDiagram]) -> PlanarDiagram | set | list | tuple:
    """
    Compute the canonical form of an *unoriented* planar diagram.

    Strategy:
      1) If the diagram is disconnected, canonicalize each component and
         reassemble in canonical order.
      2) Choose starting endpoints among nodes with minimal degree and
         minimal neighbor-sequence; run CCW BFS to produce a relabeling.
      3) For each start, relabel, then canonically permute node endpoints so
         the first visited position becomes canonical; keep the lexicographically
         minimal diagram among all starts.

    Warning:
        Canonical form may be ambiguous for diagrams containing degree-2 vertices.

    Args:
        k: A `PlanarDiagram` or a collection (set/list/tuple/iterable) thereof.

    Returns:
        The canonical `PlanarDiagram`, or a collection with each element canonicalized.

    Example:
        >>> import knotpy as kp
        >>> k = kp.from_pd_notation("[1,4,2,5], [3,6,4,1], [5,2,6,3]")
        >>> k
        Diagram a → X(b3 b2 c1 c0), b → X(c3 c2 a1 a0), c → X(a3 a2 b1 b0)
        >>> k_canonical = kp.canonical(k)
        >>> k_canonical
        Diagram a → X(b3 b2 c3 c2), b → X(c1 c0 a1 a0), c → X(b1 b0 a3 a2)
        >>> k_canonical == kp.knot("3_1")
        True

    Raises:
        TypeError: If a non-diagram is provided.
        ValueError: If the input diagram is not connected when expected.
    """
    from knotpy.algorithms.naming import number_to_alpha

    # Handle collections
    if isinstance(k, (set, list, tuple)):
        return type(k)(canonical(d) for d in k)
    if isinstance(k, Iterable) and not isinstance(k, PlanarDiagram):
        return [canonical(d) for d in k]

    if not isinstance(k, PlanarDiagram):
        raise TypeError(f"Cannot put a {type(k)} instance into canonical form.")

    if len(k) == 0:
        return k.copy()

    # Node name supply: a,b,...,z,A,...,Z,aa,ab,...
    if len(k) <= len(ascii_letters):
        letters = list(ascii_letters[: len(k)])
    else:
        letters = [number_to_alpha(i) for i in range(len(k))]

    # Disconnected case: canonicalize components and merge canonically
    if number_of_disjoint_components(k) >= 2:
        old_name = getattr(k, "name", None)
        comps = [canonical(c) for c in disjoint_union_decomposition(k)]
        ds = disjoint_union(*sorted(comps))
        ds.name = old_name
        return ds

    # Candidates: nodes with minimal degree, then minimal neighbor sequence
    minimal_nodes = _min_elements_by(k.nodes, k.degree)
    minimal_nodes = _min_elements_by(minimal_nodes, lambda n: neighbour_sequence(k, n))

    # Start from under-endpoints of candidate nodes
    start_eps = [ep for n in minimal_nodes for ep in _under_endpoints_of_node(k, n)]

    best = None

    for ep_start in start_eps:
        node_relabel, node_first_pos = _ccw_expand_node_names(k, ep_start, letters)

        if len(node_relabel) != len(k):
            raise ValueError("Cannot put a non-connected graph into canonical form.")

        # Relabel nodes and endpoints
        new_g = k.copy()
        new_g._nodes = {
            node_relabel[old_node]: type(old_inst)(
                [
                    type(ep)(node_relabel[ep.node], ep.position)
                    for ep in old_inst._inc
                ]
            )
            for old_node, old_inst in k._nodes.items()
        }

        _canonically_permute_nodes_with_given_first_positions(new_g, node_first_pos)

        if best is None or new_g < best:
            best = new_g

    return best


def _canonically_permute_nodes_with_given_first_positions(k: PlanarDiagram, node_first_position: dict) -> None:
    """
    Permute endpoints in-place so the first visited position is canonical.

    For crossings: if first_pos == 3, use the 180° rotation permutation [2,3,0,1].
    For vertices: rotate so that `first_pos` moves to 0.
    """
    for node in k.nodes:
        first_pos = node_first_position[node]

        if first_pos == 0 or (isinstance(k.nodes[node], Crossing) and first_pos == 3):
            continue

        if isinstance(k.nodes[node], Crossing):
            permutation = [2, 3, 0, 1]
        else:
            deg = k.degree(node)
            permutation = [(i - first_pos) % deg for i in range(deg)]

        permute_node(k, node, permutation)


# (Unused helper retained for reference; keep if other code imports it.)
def _canonically_permute_nodes(k: PlanarDiagram) -> None:
    """
    Uniquely permute endpoints per node so the smallest neighbor appears first.

    Note:
        This is for unoriented diagrams only.
    """
    if k.is_oriented():
        raise NotImplementedError("Canonical permutation not implemented for oriented diagrams.")

    for node in sorted(k.nodes):
        deg = k.degree(node)
        neighbors = [ep.node for ep in k.nodes[node]]

        if isinstance(k.nodes[node], Crossing):
            idx = 0 if neighbors < (neighbors[2:] + neighbors[:2]) else 2
        else:
            rotations = [neighbors[i:] + neighbors[:i] for i in range(deg)]
            idx = rotations.index(min(rotations))

        permute_node(k, node, {i: (i - idx) % deg for i in range(deg)})


if __name__ == "__main__":
    pass