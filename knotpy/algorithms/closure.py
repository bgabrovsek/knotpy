"""Disjoint components are the diagram components that do not share a common node (crossing, vertex, ...).
"""

__all__ = ['number_of_disjoint_components', 'disjoint_components',
           'add_unknot_in_place', "number_of_unknots", "remove_unknots"
           ]
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

import warnings
from string import ascii_letters
from itertools import combinations, permutations

import knotpy as kp
from knotpy.algorithms.node_operations import name_for_new_node
from knotpy.classes.endpoint import Endpoint, IngoingEndpoint, OutgoingEndpoint
from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.utils.equivalence import EquivalenceRelation


def virtual_closure(k: PlanarDiagram):
    vertices = None