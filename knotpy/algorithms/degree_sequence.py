from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.utils.set_utils import LeveledSet

def degree_sequence(k: PlanarDiagram) -> tuple:
    """
    Compute and return the degree sequence of all nodes in a given PlanarDiagram.
    
    Args:
        k (PlanarDiagram): The input planar diagram, where each node has a certain degree 
                           representing the number of endpoints connected to it.
    
    Returns:
        tuple: A tuple containing the sorted degree sequence (in ascending order) of nodes in the 
               planar diagram.
    """
    return tuple(sorted([k.degree(node) for node in k.nodes]))  


def neighbour_sequence(k: PlanarDiagram, node) -> tuple:
    """
    Computes the neighbor sequence for a given node in a PlanarDiagram.

    Args:
        k (PlanarDiagram): The PlanarDiagram object containing nodes and edges.
        node: Starting node for which the neighbor sequence is computed.

    Returns:
        tuple: A tuple where each element represents the size of a neighbor
            layer in the sequence, starting from the initial node.

    """

    seq = LeveledSet([node])

    while seq[-1]:
        seq.new_level()
        seq.extend([ep.node for node in seq[-2] for ep in k.nodes[node]])

    return tuple(len(l) for l in seq.levels[:-1])