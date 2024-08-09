" find positions for Reidemeister moves"

from itertools import chain, product, combinations
from random import choice
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.notation.pd import from_pd_notation
from knotpy.classes.node import Crossing
from knotpy.classes.endpoint import Endpoint
from knotpy.algorithms.node_operations import name_for_new_node
from knotpy.algorithms.components_disjoint import add_unknot
from knotpy.algorithms.structure import kinks

#_all__ = ['find_reidemeister_1_unkinks', "find_reidemeister_1_kinks", "find_reidemeister_3_nonalternating_triangles"]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@fs.uni-lj.si>'


def find_reidemeister_1_unkinks(k: PlanarDiagram):
    """A "unkink" position is en endpoint defining the 1-face of the diagram
    :param k:
    :return: set of endpoints
    """
    return kinks(k)


def find_reidemeister_1_kinks(k: PlanarDiagram):
    """Get positions of possible kinks. Such a position is defined as a pair (endpoint, sign), where sign is 1 or -1.
    :param k:
    :return: generator over elements of the form (endpoint, sign)
    """
    for ep, sign in product(k.endpoints, (1, -1)):  # could we just return the product?
        yield ep, sign


def find_reidemeister_2_unpokes(k: PlanarDiagram):
    """An iterator (generator) over bigon areas/regions that enable us to unpoke (Reidemeister II move). (to reduce the
    number of crossings by 2)
    The areas contain the two endpoints that define it.
    :param k: planar diagram
    :return: an iterator (generator) over poke faces
    """
    # loop through all faces and yield bigons with same position parity
    for face in k.faces:
        if (len(face) == 2 and
                all(isinstance(k.nodes[ep.node], Crossing) for ep in face) and
                face[0].position % 2 != face[1].position % 2):
            yield face


def find_reidemeister_2_pokes(k: PlanarDiagram):
    """A reidemeister poke position is the pair (over endpoint, under endpoint), where both endpoints lie in the same face.
    :param k:
    :return: generator over pairs of endpoints
    """
    for face in k.faces:
        for ep_over, ep_under in combinations(face, 2):
            yield ep_over, ep_under
            yield ep_under, ep_over  # switch over/under


def find_reidemeister_3_triangles(k):
    """An iterator (generator) over non-alternating triangular regions that enable us to perform an (Reidemeister III
    move). See also regions().
    :param k: planar diagram object
    :return: an iterator (generator) over non-alternating triangles
    """
    # TODO: make faster by not iterating over all regions
    for r in k.faces:
        if len(r) != 3 or len({ep.node for ep in r}) != 3:
            continue


        if all(type(k.nodes[ep.node]) is Crossing for ep in r) and \
                not (r[0].position % 2 == r[1].position % 2 == r[2].position % 2):
            yield r


def choose_reidemeister_1_unkink(k: PlanarDiagram, random=False):
    """
    :param k: planar diagram
    :param random: if True, the function returns a random ..., otherwise it returns the first ... is finds
    :return: ... or None
    """
    try:
        if random:
            return choice(tuple(find_reidemeister_1_unkinks(k)))
        else:
            for ep in k.endpoints:
                if isinstance(k.nodes[ep.node], Crossing) and k.nodes[ep.node][(ep.position - 1) % 4] is ep:
                    return ep

            #return next(iter(find_reidemeister_1_unkinks(k)))  # select 1st item
    except (StopIteration, IndexError):
        return None


def choose_reidemeister_1_kink(k: PlanarDiagram, random=False):
    """
    :param k: planar diagram
    :param random: if True, the function returns a random ..., otherwise it returns the first ... is finds
    :return: ... or None
    """
    try:
        if random:
            return choice(tuple(find_reidemeister_1_kinks(k)))
        else:
            return next(iter(find_reidemeister_1_kinks(k)))  # select 1st item
    except (StopIteration, IndexError):
        return None

def choose_reidemeister_2_unpoke(k: PlanarDiagram, random=False):
    """
    :param k: planar diagram
    :param random: if True, the function returns a random ..., otherwise it returns the first ... is finds
    :return: ... or None
    """
    try:
        if random:
            return choice(tuple(find_reidemeister_2_unpokes(k)))
        else:
            for ep in k.endpoints:
                if isinstance(k.nodes[ep.node], Crossing):
                    next_ep = k.nodes[ep.node][(ep.position - 1) % 4]
                    if (isinstance(k.nodes[next_ep.node], Crossing)
                            and ep.node != next_ep.node
                            and ep.position % 2 != next_ep.position % 2
                            and k.nodes[next_ep.node][(next_ep.position - 1) % 4] == ep):
                        return ep, next_ep
                        #if k.nodes[next_ep.node][(ep.position - 1) % 4] ==

            return next(iter(find_reidemeister_2_unpokes(k)))  # select 1st item
    except (StopIteration, IndexError):
        return None


def choose_reidemeister_2_poke(k: PlanarDiagram, random=False):
    """
    :param k: planar diagram
    :param random: if True, the function returns a random ..., otherwise it returns the first ... is finds
    :return: ... or None
    """
    try:
        if random:
            return choice(tuple(find_reidemeister_2_pokes(k)))
        else:
            return next(iter(find_reidemeister_2_pokes(k)))  # select 1st item
    except (StopIteration, IndexError):
        return None


def choose_reidemeister_3_nonalternating_triangle(k, random=False):
    """
    :param k: planar diagram
    :param random: if True, the function returns a random ..., otherwise it returns the first ... is finds
    :return: ... or None
    """
    try:
        if random:
            return choice(tuple(find_reidemeister_3_triangles(k)))
        else:
            return next(iter(find_reidemeister_3_triangles(k)))  # select 1st item
    except (StopIteration, IndexError):
        return None





if __name__ == "__main__":
    k = from_pd_notation("X[0,1,2,3],X[4,1,5,6],X[3,2,6,5],V[0],V[4]")
    print(k)
    if choose_reidemeister_2_unpoke(k) is None:
        print("no R2")
    for x in find_reidemeister_2_unpokes(k):
        print(x)

    pass

# OLD CODE

# def pokes(k):
#     """An iterator (generator) over bigon regions that enable us to unpoke (Reidemeister II move). The regions contain
#     the two endpoints that define it. See also regions().
#     :param k: planar diagram object
#     :return: an iterator (generator) over poke regions.
#     """
#     visited_nodes = set()
#     for node in k.crossings:
#         visited_nodes.add(node)
#         for ep in k.crossings[node]:
#             adj_ep = k.nodes[ep.node][(ep.position + 3) & 3]  # the cw endpoint
#             # the adjacent crossing must not be already visited and must not be the same (not a kink),
#             # the cw rotation of the ccw adjacent endpoint must be the original endpoint and parities do not match
#             if ep.node not in visited_nodes and adj_ep.node == node != ep.node and \
#                     k.nodes[ep.node].is_crossing() and (adj_ep.position + ep.position) & 1:
#                 yield [ep, adj_ep]



