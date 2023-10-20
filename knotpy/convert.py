from copy import deepcopy

# from knotpy.classes.spatialgraph import SpatialGraph
# from knotpy.classes.planargraph import PlanarGraph

__all__ = ['to_knotted']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek <bostjan.gabrovsek@fs.uni-lj.si>'


def to_knotted(g, create_using=None):
    """Converts a structure without crossings (PlanarGraph) to the corresponding structure with crossings
    (SpatialGraph).
    :param g: input graph-like structure
    :param create_using:
    :return: knotted structure
    """
    if isinstance(g, PlanarGraph) or isinstance(g, SpatialGraph):
        create_using = create_using or g.to_knotted_class() or SpatialGraph
        return g.copy(copy_using=create_using)

    # G.add_edges_from(
    #     (u, v, deepcopy(data))
    #     for u, nbrs in self._adj.items()
    #     for v, data in nbrs.items()
    # )


if __name__ == "__main__":
    print("Convert")
    pl = "bcde,afgc,abgd,acge,adf,beg,bfdc"  # plantri graph
    from knotpy.notation.plantri import from_plantri_notation
    g = from_plantri_notation(pl)
    print(g)
    print("...")
    k = to_knotted(g)

    print(k)

    for a in k.arcs:
        print(a)