from math import pi
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.drawing.draw_matplotlib import draw, plt, circlepack_layout
from knotpy.utils.geometry import Segment, PolySegment
from knotpy.drawing.dynamic_network import Network, animate_simulation, plot_static_frame, simulation

def _vector_to_segment(p: complex, z1: complex, z2: complex):
    """Return distance between point p and line defined by z1 and z2. Also return the vector from p to the line."""
    v = z2 - z1
    w = p - z1
    if v == 0:
        return z1 - p
    t = (w * v.conjugate()).real / abs(v)**2
    proj_p = z1 + t * v if 0 < t < 1 else (z1 if t <= 0 else z2)
    perp_vec = proj_p - p
    return abs(perp_vec), perp_vec


def init_network(k: PlanarDiagram):
    n = 3  # number of points per edge
    network = Network(ideal_bond_length=1.0)
    layout = circlepack_layout(k)  # initial layout

    # add points, connections,...
    node_neighbours = {node: [None] * k.degree(node) for node in k.nodes}  # store ccw neighbour points of node
    for arc in k.arcs:
        ep1, ep2 = arc

        # # add points
        # network.add_point(layout[ep1.node].center, name=ep1.node)
        # network.add_point(layout[ep2.node].center, name=ep2.node)

        # add arcs
        ps = PolySegment([layout[ep1.node].center, layout[arc].center, layout[ep2.node].center])
        points = ps.sample(n)
        point_names = list(zip(points, [ep1.node] + [(arc, i) for i in range(n - 2)] + [ep2.node]))
        # add bonds
        network.add_connections_from(zip(point_names, point_names[1:]))
        point_names = [_[1] for _ in point_names]
        # add stiff triplets
        network.add_stiff_triplets_from(zip(point_names, point_names[1:], point_names[2:]))

        # add angled triplets at vertices
        node_neighbours[ep1.node][ep1.position] = point_names[1]
        node_neighbours[ep2.node][ep2.position] = point_names[-2]

    for node in k.nodes:
        endpoints_ccw = node_neighbours[node]
        for ep_name_1, ep_name_2 in zip(endpoints_ccw, endpoints_ccw[1:]+endpoints_ccw[:1]):
            network.add_angled_triplet((ep_name_1, node, ep_name_2), angle=2 * pi / k.degree(node))



    return network



# def frame_stabili(values, window=5, tolerance=0.05):
#     n = len(values)
#     for i in range(n - window):
#         window_values = values[i:i + window]
#         avg = sum(window_values) / window
#         max_dev = max(abs(v - avg) for v in window_values)
#         if max_dev < tolerance:
#             return i
#     return None  # not stabilized

# def test_dynamics():
#     results = []
#     from itertools import product
#     import statistics
#     from knotpy.utils.multiprogressbar import Bar
#     bond_forces = [0.01, 0.1, 0.2, 0.5, 0.75, 1.0, 1.5, 2.0, 5.0, 10.0, 20.0, 50.0]
#     angle_forces = [0.01, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0, 1.5, 2.0, 5.0, 10.0, 20.0, 50.0]
#     stiff_forces =    [0.01, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0, 1.5, 2.0, 5.0, 10.0, 20.0, 50.0]
#     dts = [0.01, 0.05, 0.1, 0.2, 0.5]
#     repulsive_forces = [1.0]
#
#     all = len(bond_forces) * len(angle_forces) * len(stiff_forces) * len(repulsive_forces) * len(dts)
#
#     for b, a, s, r, dt in Bar(product(bond_forces, angle_forces, stiff_forces, repulsive_forces, dts), total=all):
#         force_constants = {"bond": b, "angle": a, "stiff": s, "repul": 0.1}
#         k = PlanarDiagram("9_21")
#         network = Network(ideal_bond_length=1.0)
#         init_network(k, network)
#         network.scale(1.0 / network.average_connection_length())
#         stability = simulation(network, dt=dt, force_constants=force_constants, show=False)
#         mean = statistics.mean(stability[-10:])
#         std = statistics.stdev(stability[-10:])
#         index = frame_stabili(stability)
#         results.append(
#             (mean, std, index, force_constants)
#         )
#
#     print("results")
#     results = sorted(results, key=lambda x: (x[0], x[1], x[2]))
#     for r in results[:30]:
#         print(r)
#     results = sorted(results, key=lambda x: (x[0], x[1], x[2]))
#     for r in results[500:530]:
#         print(r)
#
#     for r in results[1000:1030]:
#         print(r)
#
#     for r in results[-30:]:
#         print(r)



if __name__ == "__main__":

    import knotpy as kp

    code = "V[0,1,2],V[3,4,5],X[6,7,8,9],X[10,8,7,1],X[11,12,13,14],X[2,15,11,16],X[17,18,19,13],X[20,21,22,23],X[18,22,21,24],X[25,26,23,27],X[24,20,26,25],X[27,17,12,15],X[28,14,19,29],X[16,28,29,30],X[9,31,32,33],X[10,5,34,31],X[35,36,37,33],X[38,39,40,36],X[41,42,43,35],X[39,38,43,44],X[45,41,46,47],X[32,48,47,46],X[34,49,50,48],X[44,42,45,50],X[37,51,52,53],X[51,54,55,52],X[53,55,54,40],X[56,57,49,58],X[57,56,59,60],X[60,59,58,4],X[0,30,6,3]"

    #code = "a=X(d1 j0 j3 k2) b=X(k3 j2 i3 k0) c=X(f1 e0 i0 f2) d=X(e2 a0 k1 g2) e=X(c1 f0 d0 g1) f=X(e1 c0 c3 j1) g=X(h1 e3 d3 h2) h=X(i1 g0 g3 i2) i=X(c2 h0 h3 b2) j=X(a1 f3 b1 a2) k=X(b3 d2 a3 b0) ['name'='L11n345.11']"

    k = kp.from_pd_notation(code)
    #k = PlanarDiagram("13a_4")
    net = init_network(k)
    animate_simulation(net)


    #
    # network = Network(ideal_bond_length=1.0)
    #
    # init_network(k, network)
    #
    # print(network)
    # print(network.average_connection_length())
    # network.scale(1.0 / network.average_connection_length())
    #
    # print("Minimal", min(network.distances()))
    # print("Average", network.average_connection_length())
    # print("Maximal", max(network.distances()))
    #
    #
    # print("points:", len(network.names))
    # print("edges:", len(network.connections))
    # print("triplets:", len(network.angled_triplets))
    #
    # #for t in network.triplets:
    #     #z1, z2, z3 = [network.positions[_] for _ in t]
    #     #print("angle", math.degrees(_angle(z1, z2, z3)))
    #
    # #plot_static_frame(network, show_indices=True)
    # animate_simulation(network)
    #
