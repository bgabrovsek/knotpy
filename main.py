#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main tests for PlanarDiagram class...
"""

class a:
    def __init__(self):
        print("a")

class b:
    def __init__(self):
        print("b")

class c:
    def __init__(self):
        print("c")


class x(a,b,c):
    def __init__(self):
        a.__init__(self)
        b.__init__(self)
        c.__init__(self)
        print("x")


import knotpy as kp

if __name__ == '__main__':

    y = x()
    raise NotImplementedError("Do not run from main.")