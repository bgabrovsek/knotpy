
from knotpy.notation.pd import from_pd_notation
from knotpy.algorithms.sanity import sanity_check
from knotpy.classes.node import Crossing, Vertex
from knotpy.classes.planardiagram import PlanarDiagram



def _expand_over_under_adjacent_positions(k:PlanarDiagram, v:Vertex, start_position:int):
    """
    For a vertex and position, it checks next positions CCW and CW so that all of them form a non-alternating triangle,
    which means there is an over- or under-strand between them.

    Basically, it returns the positions of a vertex v that are incident to crossings such that a R4 slide can be
    performed, meaning, we can slide the strand from return positions to new on the "other side" of the vertex.
    it finds only such positions, where "start position" is included.

    """
    deg = k.degree(v)
    good_positions = [start_position]

    def _are_they_good_twins(twin_a, twin_b):
        if twin_a.node == twin_b.node:
            return False
        if not isinstance(k.nodes[twin_b.node], Crossing) or not isinstance(k.nodes[twin_a.node], Crossing):
            return False
        return twin_a.position % 2 == twin_b.position % 2

    # expand CCW
    for _ in range(deg - 1):
        position = good_positions[-1]
        next_position = (position + 1) % deg

        twin = k.nodes[v][position]
        next_twin = k.nodes[v][next_position]

        if _are_they_good_twins(twin, next_twin):
            good_positions.append(next_position)
        else:
            break

    # expand CW
    for _ in range(deg - 1):
        position = good_positions[0]
        prev_position = (position - 1) % deg

        twin = k.nodes[v][position]
        prev_twin = k.nodes[v][prev_position]

        if _are_they_good_twins(twin, prev_twin) and prev_position not in good_positions:
            good_positions.insert(0, prev_position)
        else:
            break

    return good_positions

def find_reidemeister_4_slides(k:PlanarDiagram):

    for v in k.vertices:
        unused_positions = set(range(deg := k.degree(v)))

        while unused_positions:
            position = unused_positions.pop()
            good_positions = _expand_over_under_adjacent_positions(k, v, position)
            yield [k.endpoint_from_pair((v, p) for p in good_positions)]
            unused_positions.difference_update(good_positions)

def reidemeister_4_slide(k, endpoints):
    pass
