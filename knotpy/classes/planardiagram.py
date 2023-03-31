#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PlanarDiagram class.
"""

__all__ = ['PlanarDiagram']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

#from functools import cached_property
import knotpy
from knotpy import convert


class PlanarDiagram:
    """
    Base class for a planar diagram.
    """

    def __init__(self, incoming_pd_data=None, **attr):
        """Initialize with ..., or planar diagram attributes (name, ...)"""

        self._inc = dict()  # list of incident arcs
        self._node = dict()  # dictionary of node attributes
        self._arc = dict()  # dictionary of arc attributes
        self._area = dict()  # dictionary of area attributes

        if incoming_pd_data is not None:
            convert.to_pd(incoming_pd_data, create_using=self)

        self.attr = dict()
        self.attr.update(attr)
        pass

    def add_node(self, node_for_adding=None, incident_arcs_ccw=(), **attr):
        """
        :param node_for_adding:
        :param incident_arcs_ccw:
        :param attr:
        :return:
        """

        # if node index not specified, take next available integer
        if node_for_adding is None:
            node_for_adding = max(self._node) + 1 if self._node else 0

        # add nodes that are adjacent to node_for_adding and not yet in self._node
        for a in incident_arcs_ccw:
            self.add_arc(a)

        if node_for_adding not in self._node:
            self._node[node_for_adding] = dict()

        self._inc[node_for_adding] = list(incident_arcs_ccw)
        self._node[node_for_adding].update(**attr)  # add attributes to node


    def add_arc(self, arc_for_adding, **attr):
        """
        :param arc_for_adding:
        :param attr:
        :return:
        """
        self._arc[arc_for_adding] = dict()
        self._arc[arc_for_adding].update(**attr)

    def add_area(self, area_for_adding, **attr):
        """
        :param area_for_adding:
        :param attr:
        :return:
        """
        self._area[area_for_adding] = dict()
        self._area[area_for_adding].update(**attr)

    def clear(self):
        """Remove all data from planar diagram.
        """
        self._node.clear()
        pass

    @property
    def name(self):
        """String identifier of planar diagram.
        """
        return self.attr.get("name", "")

    def number_of_nodes(self):
        return len(self._node)

    @property
    def framing(self):
        """(Blackboard) framing number of planar diagram.
        """
        return self.attr.get("framing", 0)

    @name.setter
    def name(self, s):
        """Set planar diagram name.
        """
        self.attr["name"] = s

    @framing.setter
    def framing(self, n):
        """Set (blackboard) framing of planar diagram."""
        self.attr["framing"] = n


    def __repr__(self):
        return "".join(
            [
                type(self).__name__,
                f" named {self.name}" if self.name else "",
                f" with nodes {str(self._inc)}",
                f" having data {str(self._node)}",
                f" and edge data {str(self._arc)}"
            ]
        )

    def __str__(self):
        return "".join(
            [
                type(self).__name__,
                f" named {self.name}" if self.name else "",
                f" with {self.number_of_nodes()} nodes"
            ]
        )

"""
p = SpatialGraph(name="Myname", lala="bitmap")
print(p.name)
p.framing = 442
print(p.framing)
"""

