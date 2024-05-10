"""
Determine what knotted structure a planar diagram is.
"""
__all__ = ['is_knot'
           ]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes.node import Crossing


def is_knot(k: PlanarDiagram) -> bool:
    return all(type(node) is Crossing for node in k.nodes)
