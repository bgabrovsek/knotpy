"""Generators for some simple planar diagrams."""

#__all__ = [""]

from knotpy.classes.planardiagram import PlanarDiagram


def empty_pd(n=0, create_using=None):
    """Returns the empty planar diagram with n nodes and zero arcs."""

    if create_using is None:
        pd = PlanarDiagram()
    elif type(create_using) is type:
        pd = create_using()
    elif not hasattr(create_using, "adj"):
        raise TypeError("create_using is not a valid PlanarDiagram  type or instance")
    else:
        # create_using is a PD style SpacialGraph
        create_using.clear()
        pd = create_using

    pd.add_nodes(n)
    return pd


def trivial_theta_curve(crate_using=None):
    pd = PlanarDiagram()
    pd.add_node(0, (0, 2, 1))
    pd.add_node(1, (0, 1, 2))
    return pd
