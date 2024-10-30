from collections import Counter


def sanity_check(k):

    _print = False

    fac = list(k.faces)
    ept = list(k.endpoints)
    arc = list(k.arcs)
    nod = list(k.nodes)

    for n in nod:
        for i in range(len(k.nodes[n])):
            if k.nodes[n][i] is None:
                raise ValueError(f"None endpoint found in node {n} at position {i}.")

    if len(ept) != len(set(ept)):
        repeated_elements = [element for element, count in Counter(ept).items() if count > 1]

        raise ValueError(f"Endpoints {repeated_elements} repeat")

    # if len(ept) == len(set.union(*[set(r) for r in fac])):
    #     raise ValueError("Not all endpoints are on faces")

    if len(ept) != len(arc)*2:
        raise ValueError(f"There are more endpoints than twice the arcs. \nKnot: {k} \n endpoints: {ept}\n arcs {arc}."
                         f"\n num. endpoints {len(ept)}, num. arcs: {len(arc)}")

    if set(ep.node for ep in ept) != set(nod):
        raise ValueError("Not all nodes have endpoints")

    for ep in ept:
        twin = k.twin(ep)
        twin_twin = k.twin(twin)
        if twin_twin != ep:
            raise ValueError("Twin of twin is not the original endpoint")

    return True