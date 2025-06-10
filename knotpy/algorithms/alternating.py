"""
Alternating
"""
from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.node.crossing import Crossing
from knotpy.algorithms.topology import edges

def _parity_diff(lst, cyclic=False):
    """Return difference of consecutive elements (mod 2) of a list."""
    if cyclic:
        return [(b - a) % 2 for a, b in zip(lst, lst[1:] + lst[:1])]
    else:
        return [(b - a) % 2 for a, b in zip(lst, lst[1:])]

def is_alternating(k: PlanarDiagram):

    def _is_edge_alternating(_edge):
        starts_with_crossing = isinstance(k.nodes[_edge[0].node], Crossing) and isinstance(k.nodes[_edge[-1].node], Crossing) and _edge[0].node == _edge[-1].node  # last two conditions are redundant
        if starts_with_crossing:
            return all(_ == 1 for _ in _parity_diff(_parity_diff([ep.position for ep in _edge], cyclic=True), cyclic=True))
        else:
            return all(_ == 1 for _ in _parity_diff(_parity_diff([ep.position for ep in _edge[1:-1]], cyclic=starts_with_crossing), cyclic=starts_with_crossing))

    return all(_is_edge_alternating(edge) for edge in edges(k))


def alternating_crossings(k: PlanarDiagram):
    """Return the set of crossings that have at least two alternating neighbours."""
    return [c for c in k.crossings
            if k.nodes[c][0].position % 2 and k.nodes[c][2].position % 2 and k.nodes[c][0].node != c and k.nodes[c][2].node != c
            or
            not k.nodes[c][1].position % 2 and not k.nodes[c][3].position % 2 and k.nodes[c][1].node != c and k.nodes[c][3].node != c
            ]

def is_face_alternating(face):
    return all(ep.position % 2 == face[0].position % 2 for ep in face)

if __name__ == "__main__":
    # print(p := _parity_diff([1, 1,0,0,3,5,4,8,1]))
    # print(_parity_diff(p))
    #
    # print(p := _parity_diff([1,1,1,1,1,1]))
    # print(_parity_diff(p))
    # print(p := _parity_diff([4,4,4,4,4,4,4,1]))
    # print(_parity_diff(p))



    import knotpy as kp
    k = kp.knot("7_3")
    print(k)
    print(is_alternating(k))
    print()

    k = kp.knot("8_19")
    print(k)
    print(is_alternating(k))
    print()

    k = kp.theta("-t5_7")
    print(k)
    print(is_alternating(k))
