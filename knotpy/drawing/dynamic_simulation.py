
"""
Dynamic simulation scaffolding for knot/graph layouts.

This module builds a bead–spring `Network` from a `PlanarDiagram` using the
circle-packing layout as an initial embedding. The network is then suitable
for dynamic relaxation (e.g., via `animate_simulation`).

The construction samples each arc by a short polyline, links consecutive
samples with bonds, adds chain stiffness triplets, and sets angular
constraints at vertices based on their degree.
"""

from math import pi
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.drawing.layout_circle_packing import layout_circle_packing
from knotpy.utils.geometry import PolySegment
from knotpy.drawing.dynamic_network import Network, animate_simulation

__all__ = [
    "init_network",
]

__version__ = "0.2"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"


def _vector_to_segment(p: complex, z1: complex, z2: complex):
    """Distance and perpendicular vector from a point to a segment.

    Computes the distance from point `p` to the line segment defined by `z1`
    and `z2`. Also returns the shortest vector from `p` to that segment.

    Args:
        p: Point as a complex number.
        z1: Segment start point (complex).
        z2: Segment end point (complex).

    Returns:
        tuple[float, complex]: (distance, vector) where `vector` points from `p`
        to the closest point on the segment.
    """
    v = z2 - z1
    w = p - z1
    if v == 0:
        perp_vec = z1 - p
        return abs(perp_vec), perp_vec
    t = (w * v.conjugate()).real / (abs(v) ** 2)
    proj_p = z1 + t * v if 0 < t < 1 else (z1 if t <= 0 else z2)
    perp_vec = proj_p - p
    return abs(perp_vec), perp_vec


def init_network(k: PlanarDiagram) -> Network:
    """Initialize a dynamic bead–spring network from a planar diagram.

    Each arc (ep1—ep2) is represented by a short polyline sampled from a
    `PolySegment` through [center(ep1.node), center(arc), center(ep2.node)].
    Consecutive samples are connected by bonds; consecutive triples form
    stiffness constraints. For each vertex, adjacent incident samples define an
    angular constraint with the ideal angle 2π / degree(vertex).

    Args:
        k: Input planar diagram.

    Returns:
        Network: A constructed bead–spring network ready for simulation.
    """
    samples_per_arc = 3  # number of points per arc polyline
    network = Network(ideal_bond_length=1.0)

    # Initial embedding (centers of circles for nodes/arcs)
    layout = layout_circle_packing(k)

    # For each node, remember the sample point nearest to each incident endpoint (CCW order)
    node_neighbours = {node: [None] * k.degree(node) for node in k.nodes}

    for arc in k.arcs:
        ep1, ep2 = arc

        # Build a simple polyline through node center – arc center – node center

        ps = PolySegment([layout[ep1.node], layout[arc].center, layout[ep2.node]])
        points = ps.sample(samples_per_arc)

        # Name samples: endpoints by node name, internal samples by (arc, i)
        point_names = list(zip(points, [ep1.node] + [(arc, i) for i in range(samples_per_arc - 2)] + [ep2.node]))

        # Bonds between consecutive samples
        network.add_connections_from(zip(point_names, point_names[1:]))

        # Stiffness triplets along the sampled polyline
        name_seq = [name for _, name in point_names]
        network.add_stiff_triplets_from(zip(name_seq, name_seq[1:], name_seq[2:]))

        # Remember inner samples adjacent to each vertex (for angle constraints)
        node_neighbours[ep1.node][ep1.position] = name_seq[1]
        node_neighbours[ep2.node][ep2.position] = name_seq[-2]

    # Add angular constraints at vertices
    for node in k.nodes:
        ccw = node_neighbours[node]
        ideal = 2 * pi / k.degree(node)
        for a, b in zip(ccw, ccw[1:] + ccw[:1]):
            network.add_angled_triplet((a, node, b), angle=ideal)

    return network


if __name__ == "__main__":
    # Small demo
    import knotpy as kp

    code = "V[0,1,2],V[3,4,5],X[6,7,8,9],X[10,8,7,1],X[11,12,13,14],X[2,15,11,16],X[17,18,19,13],X[20,21,22,23],X[18,22,21,24],X[25,26,23,27],X[24,20,26,25],X[27,17,12,15],X[28,14,19,29],X[16,28,29,30],X[9,31,32,33],X[10,5,34,31],X[35,36,37,33],X[38,39,40,36],X[41,42,43,35],X[39,38,43,44],X[45,41,46,47],X[32,48,47,46],X[34,49,50,48],X[44,42,45,50],X[37,51,52,53],X[51,54,55,52],X[53,55,54,40],X[56,57,49,58],X[57,56,59,60],X[60,59,58,4],X[0,30,6,3]"
    k = kp.from_pd_notation(code)
    net = init_network(k)
    animate_simulation(net)
