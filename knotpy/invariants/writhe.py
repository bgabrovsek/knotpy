__all__ = ['writhe']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@fs.uni-lj.si>'

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.algorithms.components_disjoint import number_of_disjoint_components
from knotpy.algorithms.orientation import all_orientations, oriented

def writhe(k: PlanarDiagram) -> int:
    """The writhe is the total number of positive crossings minus the total number of negative crossings.
    :param k:
    :return:
    """

    # TODO: orient if one component, otherwise raise error
    if not k.is_oriented():
        if number_of_disjoint_components(k) != 1:
            raise ValueError(f"Cannot determine the writhe of a unoriented link with {number_of_disjoint_components(k)} disjoint components")
        else:
            k = oriented(k)


    return sum(k.nodes[node].sign() for node in k.crossings)
