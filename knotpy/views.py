"""
The views are read-only iterable containers that are updated as the planar diagram is updated.
As with dicts, the graph should not be updated while iterating through the view.
"""

from collections.abc import Mapping, Set

import knotpy as kp

__all__ = [
    "ArcView",
#    "DegreeView",
]


# NodeViews
class ArcView(Mapping):
    """ArcView class to act as pd.arcs for a planar diagram.
    Iteration is over arcs.
    """

    #__slots__ = ("_nodes",)
    pass