from sympy import expand, Integer, symbols, Symbol
from itertools import product

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.algorithms.orientation import orient
from knotpy.algorithms.skein import smoothen_crossing
from knotpy.algorithms.naming import unique_new_node_name
from knotpy.classes.endpoint import OutgoingEndpoint
from knotpy.algorithms.disjoint_union import add_unknot
from knotpy.invariants.writhe import writhe
from knotpy.reidemeister.reidemeister import make_all_reidemeister_moves

__all__ = ['arrow_polynomial']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>'

_A = symbols("A")

def disoriented_smoothing(k: OrientedPlanarDiagram, crossing):
    """
    See https://arxiv.org/pdf/1602.03579, page 40, Figure 36.
    :param k:
    :param crossing:
    :return:
    """

    node_inst = k.nodes[crossing]
    pos = 0 if type(node_inst[0]) == type(node_inst[1]) else 1  # if 0, join 0 & 1, 2 & 3, else join 1 & 2 and 3 & 0

    node0 = unique_new_node_name(k)
    k.add_vertex(node0, degree=2)
    node1 = unique_new_node_name(k)
    k.add_vertex(node1, degree=2)

    k.set_endpoint((node0, 0), node_inst[pos])
    k.set_endpoint(node_inst[pos], (node0, 0), create_using=type(node_inst[pos]).reverse_type(), acute=False)
    k.set_endpoint((node0, 1), node_inst[pos + 1], )
    k.set_endpoint(node_inst[pos + 1], (node0, 1), create_using=type(node_inst[pos + 1]).reverse_type(), acute=True)

    k.set_endpoint((node1, 0), node_inst[pos + 2])
    k.set_endpoint(node_inst[pos + 2], (node1, 0), create_using=type(node_inst[pos + 2]).reverse_type(), acute=False)
    k.set_endpoint((node1, 1), node_inst[(pos + 3) % 4])
    k.set_endpoint(node_inst[(pos + 3) % 4], (node1, 1), create_using=type(node_inst[(pos + 3) % 4]).reverse_type(), acute=True)

    k.remove_node(crossing, remove_incident_endpoints=False)


def _components_paths(k:PlanarDiagram):
    long_components = []
    circ_components = []

    available_endpoints = set(k.endpoints)

    # long components
    for ep in k.endpoints:
        if k.degree(ep.node) == 1 and type(ep) is OutgoingEndpoint:
            path = []
            while True:
                path.append(ep)
                ep = k.twin(ep)
                path.append(ep)
                if k.degree(ep.node) == 1:
                    break
                ep = k.endpoint_from_pair((ep.node, (ep.position + 1) % 2))
            long_components.append(path)
            available_endpoints = available_endpoints.difference(path)

    # circular components
    while available_endpoints:
        path = []
        ep = next(iter(available_endpoints))
        while ep in available_endpoints:
            path.append(ep)
            available_endpoints.remove(ep)
            ep = k.twin(ep)
            path.append(ep)
            available_endpoints.remove(ep)
            ep = k.endpoint_from_pair((ep.node, (ep.position + 1) % 2))
        circ_components.append(path)

    return circ_components, long_components


def _remove_consecutive_cusps(k:PlanarDiagram):

    # TODO: write better, just loop through arcs and stop when no reductions were made
    reductions_were_made = True
    while reductions_were_made:
        reductions_were_made = False
        nodes = list(k.vertices)
        for node in nodes:
            for pos in (0, 1):
                if node in k.nodes and k.degree(node) == 2:
                    ep = k.endpoint_from_pair((node, pos))  # endpoint in the "valley"
                    twin = k.twin(ep)  # the other endpoint in the "valley"
                    adj_node = twin.node  # the other node of the possible reduction
                    if k.degree(adj_node) != 2:  # should not be a terminal node
                        break
                    if ep["acute"] != twin["acute"]:
                        # if twins have different acuteness, remove them
                        ep0 = k.nodes[node][(pos + 1) % 2]
                        ep1 = k.nodes[twin.node][(twin.position + 1) % 2]

                        if ep0.node == adj_node and ep1.node == node:
                            add_unknot(k)

                        k.set_endpoint(ep0, ep1, type(ep1), acute=ep1["acute"])
                        k.set_endpoint(ep1, ep0, type(ep0), acute=ep0["acute"])
                        k.remove_node(node, remove_incident_endpoints=False)
                        k.remove_node(adj_node, remove_incident_endpoints=False)
                        reductions_were_made = True


def _generator_to_variables(k: PlanarDiagram):
    """Return a sympy expression for a reduced diagram. A reduced diagram does not have consecutive acute cusps.
    :param k:
    :return:
    """
    polynomial = Integer(1)
    _kauffman_term = (-_A ** 2 - _A ** (-2))

    circ_comp, line_comp = _components_paths(k)

    for c in circ_comp:
        polynomial *= _kauffman_term if len(c) == 2 else symbols(f"K{len(c) // 4}")
    for c in line_comp:
        polynomial *= 1 if len(c) == 2 else symbols(f"L{(len(c) - 2) // 4}")

    return polynomial


def arrow_polynomial(k: PlanarDiagram | OrientedPlanarDiagram, normalize=True):
    """Compute the arrow polynomial of a knotoid. The arrow polynomial is defined in https://arxiv.org/pdf/1602.03579.pdf,
    :param k:
    :param variable:
    :param normalize:
    :return:
    """

    polynomial = Integer(0)

    # stack_states = list()
    original_knot = k if k.is_oriented() else orient(k)
    crossings = tuple(k.crossings)
    # state expansions
    for state in product((1, -1), repeat=len(crossings)):
        k = original_knot.copy()
        for method, node in zip(state, crossings):
            if (method > 0) ^ (k.nodes[node].sign() < 0):  # "A" oriented smoothing
                smoothen_crossing(k, crossing_for_smoothing=node, method="O", inplace=True)
            else:  # "B" disoriented oriented smoothing
                disoriented_smoothing(k, node)

        _remove_consecutive_cusps(k)
        polynomial += _A ** sum(state) * _generator_to_variables(k)

    if normalize:
        polynomial *= (- _A ** 3) ** (-writhe(original_knot))  # ignore framing if normalized
    else:
        polynomial *= (- _A ** 3) ** (-original_knot.framing)

    return expand(polynomial)

if __name__ == '__main__':
    import knotpy as kp
    import matplotlib.pyplot as plt
    import sympy
    #
    # k = kp.from_pd_notation("X[0,1,2,3],X[1,4,0,2],V[3],V[5],X[4,6,6,5] ")
    # print(k)
    # o = kp.all_orientations(k)[0]
    # print(o)
    # print(arrow_polynomial(o))
    # #exit()
    #
    # # A**(-4) + L1/A**6 - L1/A**10
    # print("-------")

    k = kp.from_pd_notation("X[3,2,4,1],X[2,5,3,4],V[1],V[5]")
    print(k)
    print(ppp:=arrow_polynomial(k))
    print("---")
    # ooo = kp.all_orientations(k)
    # o = ooo[0]

    # TODO: make oriented Reidemeister moves

    for o in kp.all_orientations(k):
        print(o)
        print(arrow_polynomial(o))

    print("----")

    for k_r in make_all_reidemeister_moves(k,  depth=2):
        #print(k_r)
        for o in kp.all_orientations(k_r):
            # print(o)
            # print(kp.to_pd_notation(o))
            print(p:=arrow_polynomial(o))

            if p != ppp:
                exit()
            # print("")
            # print("")
    # ooo = kp.all_orientations(k)
    # for o in ooo:
    #     print("  ", o)
    #     poly = affine_index_polynomial(o)
    #     print(poly)

