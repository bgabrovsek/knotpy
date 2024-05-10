__all__ = ['writhe']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@fs.uni-lj.si>'

from knotpy.classes.planardiagram import PlanarDiagram


def writhe(k: PlanarDiagram) -> int:
    """The writhe is the total number of positive crossings minus the total number of negative crossings.
    :param k:
    :return:
    """

    if not k.is_oriented():
        raise NotImplementedError()
        # TODO: orient if one component, otherwise return error

    return sum(node.sign() for node in k.crossings)

