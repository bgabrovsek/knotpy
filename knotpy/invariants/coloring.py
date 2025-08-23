__all__ = ["conway"]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek <bostjan.gabrovsek@pef.uni-lj.si>"

from collections import deque

from knotpy.classes.planardiagram import Diagram
from knotpy.algorithms.attributes import clear_endpoint_attributes


def tricolorable(k:Diagram) -> int:
    pass

def colorings(k:Diagram, n:int):
    k = k.copy()
    clear_endpoint_attributes(k, "color")
    stack = deque([k])
    nodes = list(k.nodes)
    for n in nodes:
        pass


