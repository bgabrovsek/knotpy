from math import pi
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.drawing.draw_matplotlib import draw, plt, circlepack_layout
from knotpy.utils.geometry import Segment, PolySegment
from knotpy.drawing.network import Network, animate_simulation, plot_static_frame


def get_number_of_point_from_faces(k:PlanarDiagram, arc):
    ep1, ep2 = arc

    n2 = 10
    n3 = 12
    n4 = 14

    n = n4
    for face in k.faces:
        if len(face) == 2 and (ep1 in face or ep2 in face):
            # 2-faces should have 5 verticess
            n = min(n, n2)
        elif len(face) == 3 and (ep1 in face or ep2 in face):
            # 4-faces should have 6 verticess
            n = min(n, n2)

    return n

def _sample_arcs(k:PlanarDiagram, layout, network:Network):
    for arc in k.arcs:
        ep1, ep2 = arc
        n = get_number_of_point_from_faces(k, arc)
        ps = PolySegment([layout[ep1.node].center, layout[arc].center, layout[ep2.node].center])  # segments from nodes through arc center
        points = ps.sample(n)
        # names of "vertices" is node name, name of "edges" is the tuple (node 1 name, node 2 name, index)
        names = [ep1.node] + [(arc, i) for i in range(n-2)] + [ep2.node]
        point_names = list(zip(points, names))
        for a, b in zip(point_names, point_names[1:]):
            network.add_connection((a, b))

        # add stiff triplets, so the arc is straight
        for t in zip(names, names[1:], names[2:]):
            network.add_stiff_triplet(t)

    return network

def init_network(k: PlanarDiagram, network: Network):
    # get initial layout
    layout = circlepack_layout(k)

    # sample all arcs
    _sample_arcs(k, layout, network)

    # add angled triplets (vertices, crossings)
    for node in k.nodes:
        endpoints_ccw = list(k.nodes[node])
        for ep0, ep1 in zip(endpoints_ccw, endpoints_ccw[1:]+endpoints_ccw[:1]):
            arc_node0 = network.closest_endpoint_to_vertex(node, ep0)
            arc_node1 = network.closest_endpoint_to_vertex(node, ep1)
            network.add_angled_triplet((arc_node0, node, arc_node1), angle=2 * pi / k.degree(node))
    return network





if __name__ == "__main__":
    from network import _angle, _rotate
    import math
    k = PlanarDiagram("9_21")

    network = Network(ideal_bond_length=1.0)

    init_network(k, network)

    print(network)
    print(network.average_connection_length())
    network.scale(1.0 / network.average_connection_length())
    network.sanity_check()
    print("Minimal", min(network.distances()))
    print("Average", network.average_connection_length())
    print("Maximal", max(network.distances()))


    print("points:", len(network.names))
    print("edges:", len(network.connections))
    print("triplets:", len(network.angled_triplets))

    #for t in network.triplets:
        #z1, z2, z3 = [network.positions[_] for _ in t]
        #print("angle", math.degrees(_angle(z1, z2, z3)))

    #plot_static_frame(network, show_indices=True)
    animate_simulation(network)

