"""
The views are read-only iterable containers that are updated as the planar diagram is updated.
As with dicts, the graph should not be updated while iterating through the view.
"""

from collections.abc import Mapping, Set

import knotpy as kp

__all__ = [
    "RegionView",
]


# NodeViews
class RegionView(set):
    """RegionView class
    """

    def __init__(self, PG):
        super().__init__()
        PG._node

    #__slots__ = ("_nodes",)
    pass