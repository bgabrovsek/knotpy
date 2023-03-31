#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main test for PlanarDiagram class..
"""
from knotpy import *

#from igraph import *


if __name__ == '__main__':
    sg = PlanarDiagram(name="K1")
    sg.add_node(3, [3, 4, 5], color=0)
    print(repr(sg))

    pd1 = PlanarDiagram(name="theta")
    pd1.add_node(0, (0, 2, 1), weight=2)
    pd1.add_node(1, (0, 1, 2), color=3)


    print(repr(pd1))