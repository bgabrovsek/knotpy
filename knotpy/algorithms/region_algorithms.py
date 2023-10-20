from knotpy.classes.planardiagram import PlanarDiagram

# from knotpy.classes.endpoint import Endpoint

__all__ = ['regions', 'choose_kink', 'choose_poke', "check_region_sanity"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@fs.uni-lj.si>'


def regions(k: PlanarDiagram, length=None):
    """Iterates over regions (planar graph faces) of a planar diagram. A planar region is defined as a sequence of
    endpoints in the following manner: an endpoint (a, p) in a region R is the endpoint before the crossing a from R in
    ccw order, in other words, if we turn at a crossing ccw, we get the endpoint (a, p - 1), which forms an arc with
    (b, q), where (b, q) is again in R.
    The function takes the set of all endpoints, select an unused endpoint and travels along the edges, until there are no endpoints left.
    :param k: knotted object
    :param length: of the length is given, only regions of this length (order) will be considered
    """

    #print("Computing regions of", k)

    unused_endpoints = set(k.endpoints)
    while unused_endpoints:
        ep = unused_endpoints.pop()
        region = list()
        while True:
            region.append(ep)
            ep = k.nodes[ep.node][(ep.position - 1) % len(k.nodes[ep.node])]
            if ep in unused_endpoints:
                unused_endpoints.remove(ep)
            else:
                break
        if not length or len(region) == length:
            yield tuple(region)


def check_region_sanity(k: PlanarDiagram):
    """
    Check if regions do not overlap (e.g. ccw vertex order respected)
    :param k:
    :return:
    TODO: fix so it works for handcuff-like links (with a cut-edge)
    """
    def unique(s):
        return len(set(s)) == len(s)

    regs = regions(k)
    return all(unique([ep.node for ep in r]) for r in regs)


def kinks(k, of_node=None):
    """An iterator (generator) over regions of kinks/loops. The regions are singleton lists containing the endpoint.
    See also regions().
    :param k: planar diagram object
    :param of_node: if of_node is not None, only the kinks attached to the node will be given
    :return: an iterator (generator) over kink regions.
    """

    for node in k.crossings if of_node is None else (of_node,):
        for ep in k.nodes[node]:
            if ep == k.nodes[ep.node][(ep.position + 3) & 3]:  # is the endpoint and the ccw endpoint the same?
                yield [ep]


def choose_kink(k):
    """Returns the first kink region of the knotted planar diagram object k.
    :return: the singleton kink region if a kink exists, None otherwise
    """
    try:
        return next(iter(kinks(k)))
    except StopIteration:
        return None


def pokes(k):
    """An iterator (generator) over bigon regions that enable us to unpoke (Reidemeister II move). The regions contain
    the two endpoints that define it. See also regions().
    :param k: planar diagram object
    :return: an iterator (generator) over poke regions.
    """
    visited_nodes = set()
    for node in k.crossings:
        visited_nodes.add(node)
        for ep in k.crossings[node]:
            adj_ep = k.nodes[ep.node][(ep.position + 3) & 3]  # the cw endpoint
            # the adjacent crossing must not be already visited and must not be the same (not a kink),
            # the cw rotation of the ccw adjacent endpoint must be the original endpoint and parities do not match
            if ep.node not in visited_nodes and adj_ep.node == node != ep.node and \
                    k.nodes[ep.node].is_crossing() and (adj_ep.position + ep.position) & 1:
                yield [ep, adj_ep]


def choose_poke(k):
    """Returns the first bigon poke region of the knotted planar diagram object k.
    :return: the poke region of length 2 if a poke region exists, None otherwise
    """
    try:
        return next(iter(pokes(k)))
    except StopIteration:
        return None


def triangles_nonalternating(k):
    """An iterator (generator) over non-alternating triangular regions that enable us to perform an (Reidemeister III
    move). See also regions().
    :param k: planar diagram object
    :return: an iterator (generator) over non-alternating triangles
    """
    # TODO: make faster by not iterating over all regions
    for r in regions(k, length=3):
        if all(k.nodes[ep.node].is_crossing() for ep in r) and \
                not (r[0].position & 1 == r[1].position & 1 == r[2].position & 1):
            yield r

    # visited_nodes = set()
    # for node in k.crossings:
    #     visited_nodes.add(node)
    #     for ep in k.crossings[node]:
    #         adj_ep = k.nodes[ep.node][(ep.position + 3) & 3]   # the cw endpoint
    #         # the adjacent crossing must not be already visited and must not be the same (not a kink),
    #         # the cw rotation of the ccw adjacent endpoint must be the original endpoint and parities do not match
    #         if ep.node not in visited_nodes and adj_ep.node == node != ep.node and \
    #                 k.nodes[ep.node].is_crossing() and (adj_ep.position + ep.position) & 1:
    #             yield [ep, adj_ep]
