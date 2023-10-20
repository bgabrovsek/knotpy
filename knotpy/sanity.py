from knotpy.classes.knot import Knot
from knotpy.algorithms.region_algorithms import regions
from knotpy.algorithms.components import link_components_endpoints, disjoint_components

def sanity_check(k):

    _print = True

    reg = list(regions(k))
    ept = list(k.endpoints)
    arc = list(k.arcs)
    nod = list(k.nodes)
    lin = link_components_endpoints(k)
    #dis = disjoint_components(k)

    if _print:
        print("Sanity check")
        print(k)
        print("  regions", reg)
        print("  endpoints", ept)
        print("  arcs", arc)
        print("  nodes", nod)
        print("  link components", lin)
        print("  disjoint components", lin)

    if len(ept) != len(set(ept)):
        return False

    if len(ept) == len(set.union(*[set(r) for r in reg])):
        return False

    if len(ept) == len(set.union(*[set(l) for l in lin])):
        return False

    if len(ept) == len(arc)*2:
        return False

    if len(ept) == sum(len(l) for l in lin):
        return False

    #assert len(nod) == sum(len(c) for c in dis)
    # Euler characteristic
    #assert len(nod) - len(arc) + len(reg) == 2 * len(dis)