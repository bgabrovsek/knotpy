import networkx as nx
from sympy import symbols, expand
from copy import deepcopy
import math
from collections import defaultdict, deque

from  knotpy.algorithms.topology import edges


def parse_pd(s):
    """Parse planar diagram to networkx graph"""
    G = nx.MultiGraph()
    nodes = {tuple(eval(n[1:])): (n[0], i) for i, n in enumerate(s.strip().split(";"))}

    for i, n in enumerate(nodes):
        if nodes[n][0] == "X":
            G.add_node(i, ccw=list(n))
        else:
            G.add_node(i)
    arcs = defaultdict(list)
    for i, n in enumerate(nodes):
        for edge in n:
            arcs[edge].append(i)
    for a in arcs:
        G.add_edge(*arcs[a], label=a)

    return G

def yamada(G, var):
    """ Computes the Yamada of G using variable var. Updated: using a stack"""
    stack = deque()  # stack of tuples (poly, graph)
    stack.append((1, G))  # "1 * G"
    polynomial = 0

    def get_edge(label): return [e for e in knotpy.algorithms.topology.edges.edges if knotpy.algorithms.topology.edges.edges[e[0], e[1], e[2]]["label"] == label][0]
    def reattach(edge, u, v): return (v, edge[1]) if edge[0] == u else (edge[0], v)  # edge with node u to edge with v

    while stack:

        poly, G = stack.pop()

        if crossings := [n for n in G.nodes if "ccw" in G.nodes(data=True)[n]]:
            c = crossings[0]
            labels = G.nodes(data=True)[c]["ccw"]
            edges = [get_edge(l) for l in labels]

            del G.nodes[c]['ccw']  # crossing -> vertex

            # loop/kink?
            if any(labels[i] == labels[(i + 1) & 3] for i in range(4)):
                term = (var**2) if labels[0] == labels[1] or labels[2] == labels[3] else (1/(var**2))
                for i in range(4):
                    if labels[i] == labels[(i+1) & 3]:
                        G.remove_edge(*edges[i])
                        break
                stack.append((poly * term, G))
                continue

            # skein
            A = deepcopy(G)  # "A" smoothing, maybe shallow works
            B = deepcopy(G)  # "B" smoothing
            w = len(G)  # new node
            A.add_node(w)
            B.add_node(w)

            A.remove_edges_from(edges[2:])
            A.add_edge(*reattach(edges[2], c, w), label=labels[2])
            A.add_edge(*reattach(edges[3], c, w), label=labels[3])

            B.remove_edges_from(edges[1:3])
            B.add_edge(*reattach(edges[1], c, w), label=labels[1])
            B.add_edge(*reattach(edges[2], c, w), label=labels[2])

            stack.append((poly * var, A))
            stack.append((poly / var, B))
            stack.append((poly, G))
            continue

        if nx.has_bridges(G):
            continue

        # disjoint components
        if len(cc := list(nx.connected_components(G))) > 1:
            polynomial += poly * math.prod([yamada(G.subgraph(c).copy(), var) for c in cc])  # TODO: avoid recursion
            continue

        # normal edges
        if edges := [e for e in knotpy.algorithms.topology.edges.edges if e[0] != e[1]]:
            e = edges[0]  # select an edge
            C = nx.contracted_edge(G, e)
            C.remove_edge(e[0], e[0])
            G.remove_edge(*e)
            stack.append((poly, G))
            stack.append((poly, C))
            continue

        polynomial -= poly * (-var - 1 - 1/var)**len(knotpy.algorithms.topology.edges.edges)
    return polynomial

A = symbols("A")

# Example 1: Yamada's paper, Fig. 7

H = parse_pd('V(4,12,5);V(8,7,0);X(0,11,1,12);X(5,1,6,2);X(10,6,11,7);X(9,3,8,4);X(2,10,3,9)')
print(expand(yamada(H, A)))



#A**9 - A**8 - 2*A**7 + A**6 - A**5 + 2*A**3 + A**2 + 2*A + 1/A - 1/A**3 + A**(-4) + A**(-5) - 1/A**6 + A**(-7) + A**(-8)
#[-1, 2, -3, 1, 5, -9, 17, -18, 20, -16, 12, -5, 1, 1, -1]®

# Example 2: handcuff link

G = nx.MultiGraph()
G.add_node(0, ccw=[0,3,1,4])
G.add_node(1, ccw=[3,0,5,2])
G.add_node(2)
G.add_node(3)
G.add_edge(0, 1, label=0)
G.add_edge(0, 1, label=3)
G.add_edge(0, 2, label=4)
G.add_edge(0, 3, label=1)
G.add_edge(1, 2, label=5)
G.add_edge(1, 3, label=2)
G.add_edge(2, 3, label=6)

print(expand(yamada(G, A)))


# -A**5 - A**4 - A**3 - A**2 + 1/A + A**(-2) + A**(-3) + A**(-4)

