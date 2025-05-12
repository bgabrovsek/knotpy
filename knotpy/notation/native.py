"""
Default (native) KnotPy notation with all diagram information stored. It is similar to EM notation.

Notation example (without attributes):

SpatialGraph
Crossing a [('b',0),('b',2),('b',1),('v',0)]
Crossing b [('a',0),('a',2),('a',1),('u',0)]
Vertex u [('b',3)]
Vertex v [('a',3)]

Notation example (with attributes):

SpatialGraph {'name':'x1','color':'red'}
Crossing a [('b',0,{'color':'Orange'}),('b',2,{'color':'Orange'}),('b',1,{'color':'Orange'}),('v',0,{'color':'Orange'})] {'color':'blue'}
Crossing b [('a',0,{'color':'Orange'}),('a',2,{'color':'Orange'}),('a',1,{'color':'Orange'}),('u',0,{'color':'Orange'})] {'color':'blue'}
Vertex u [('b',3,{'color':'Orange'})] {}
Vertex v [('a',3,{'color':'Orange'})] {}

See "Ewing, B. & Millett, K. C. in The mathematical heritage of CF Gauss 225–266 (World Scientific, 1991)".
"""

__all__ = ["to_knotpy_notation", "from_knotpy_notation"]
__version__ = "1.0"
__author__ = "Boštjan Gabrovšek"

import re
from ast import literal_eval

from knotpy.classes.planardiagram import PlanarDiagram
from knotpy.classes import Vertex, Crossing, Node


def _attr_to_str(attr):
    """
    Convert a dictionary of attributes to a string representation.
    """
    return ",".join(f"{repr(key)}={repr(value)}" for key, value in attr.items())

def _node_to_str(node:Node):
    """
    Convert a node to a string representation.
    """
    return " ".join(f"{ep.node}{ep.position}" for ep in node)


def to_knotpy_notation(k):
    """Returns KnotPy notation of planar diagram (native python structures list, tuples, dicts,... encoding the whole
    diagram)

    Example:

    """
    _node_abbr = {Crossing: "X", Vertex: "V"}
    compact_notation = all(isinstance(node, str) and len(node) == 1 for node in k.nodes)  # what notation to use?

    if compact_notation:

        # encode nodes
        nodes_str = ""
        for node in sorted(k.nodes):
            nodes_str += str(node) + "=" + _node_abbr[type(k.nodes[node])] + "(" + _node_to_str(k.nodes[node]) + ")" + " "
        nodes_str = nodes_str[:-1]

        # encode attributes
        diagram_attr_str = _attr_to_str(k.attr)
        node_attr_str = " ".join(f"{node}:{{{_attr_to_str(k.nodes[node].attr)}}}" for node in sorted(k.nodes) if k.nodes[node].attr)
        endpoint_attr_str = " ".join(f"{ep.node}{ep.position}:{{{_attr_to_str(ep.attr)}}}" for ep in sorted(k.endpoints) if ep.attr)

        # do not provide all attributes if they do not exist
        parts = [diagram_attr_str, node_attr_str, endpoint_attr_str]
        while parts and not parts[-1]:
            parts = parts[:-1]

        if not parts:
            return f"{nodes_str}"
        else:
            return f"{nodes_str} [{'; '.join(parts)}]"



    else:
        NotImplementedError("Non-compact notation is not implemented yet (vertex names are not strings of length 1, e.g. 'a' or 'b').")
        return None

def _parse_attributes_dict(attr_string: str) -> dict:
    """
    Parse a string of key=value pairs into a dictionary using regex.

    Args:
        attr_string (str): A string like "'name'='my diagram','framing'=3"

    Returns:
        dict: A dictionary with keys and evaluated values.
    """
    pattern = re.compile(r"'?(\w+)'?\s*=\s*('[^']*'|\d+|\[.*?\]|\{.*?\})")
    result = {}
    for key, value in pattern.findall(attr_string):
        result[key] = literal_eval(value)
    return result


def _parse_compact(notation: str) -> PlanarDiagram:
    """
       Parse a custom knot diagram notation into structured components.

       Extracts nodes, their types, endpoints, diagram-level attributes,
       node attributes, and endpoint attributes from a compact string format.

       Args:
           notation (str): The knot diagram notation string.

       Returns:
           dict: A dictionary with keys:
               - 'nodes': list of node names
               - 'node_types': mapping from node to 'V' or 'X'
               - 'node_endpoints': mapping from node to list of (node, position) tuples
               - 'diagram_dict': global diagram-level attributes
               - 'node_dict': per-node attribute dictionaries
               - 'endpoint_dict': per-endpoint attribute dictionaries
       """

    if "→" in notation:
        notation = notation.replace(" → ", "=").replace("→", "=").replace("),",")")

    _node_abbr = {"X": Crossing, "V": Vertex}

    # Separate definition and attribute parts
    definition_part, *attribute_parts = notation.split('[')
    attribute_string = "[".join(attribute_parts).rstrip(']') if attribute_parts else ""

    # Parse node definitions
    node_pattern = re.compile(r'(\w+)=([VX])\(([^)]+)\)')

    k = PlanarDiagram()

    # parse diagram structure (nodes, endpoints)

    for match in node_pattern.finditer(definition_part):
        node, node_type, endpoints = match.groups()
        endpoints = endpoints.strip().split()
        k.add_node(node, create_using=_node_abbr[node_type], degree=len(endpoints))

        for pos, ep_str in enumerate(endpoints):
            pair =  tuple(re.match(r'([a-zA-Z]+)(\d+)', ep_str.strip()).groups())
            k.set_endpoint((node, pos), (pair[0], int(pair[1])))

    # parse attributes
    attr_split = attribute_string.split(";")
    if len(attr_split) > 3:
        raise ValueError("Invalid attribute string format.")
    attr_split += [""] * (3 - len(attr_split))  # if not all attribute types are given

    diagram_attr, node_attr, endpoint_attr = attr_split

    # parse diagram attributes
    k.attr.update(_parse_attributes_dict(diagram_attr.strip()))  # set diagram attributes


    # parse node attributes
    node_attribute_pattern = re.compile(r'(\w+)\s*:\s*\{([^}]*)\}')
    for node, attr_str in node_attribute_pattern.findall(node_attr):
        k.nodes[node].attr.update(_parse_attributes_dict(attr_str.strip()))

    # parse endpoint attributes
    node_attribute_pattern = re.compile(r'(\w+)\s*:\s*\{([^}]*)\}')
    for ep, attr_str in node_attribute_pattern.findall(endpoint_attr):
        pair = tuple(re.match(r'([a-zA-Z]+)(\d+)', ep).groups())
        k.endpoint_from_pair((pair[0],int(pair[1]))).attr.update(_parse_attributes_dict(attr_str.strip()))

    return k


def from_knotpy_notation(notation: str) -> PlanarDiagram:
    """
    Example: "a=V(b0 c0 d3) b=V(a0 d2 c1) c=X(a1 b2 d1 d0) d=X(c3 c2 b1 a2)"
    Args:
        notation:

    Returns:

    """


    compact_notation = True

    if compact_notation:
        return _parse_compact(notation)

    else:
        raise NotImplementedError()


# def from_knotpy_notation(text) -> PlanarDiagram:
#     data = eval(text)
#     knot_type, knot_attr, knot_nodes = data
#
#     k = eval("kp." + knot_type)()  # create the diagram
#     k.attr.update(knot_attr)  # update the attributes TODO: we can add attributes oin the construction
#
#     for node_tuple in knot_nodes:
#         node_type, node_name, node_adj, node_attr = node_tuple
#         node_degree = len(node_adj)
#         k.add_node(node_for_adding=node_name,
#                    create_using=eval("kp." + node_type),
#                    degree=node_degree)
#         k.nodes[node_name].attr.update(node_attr)  # TODO: we can add attributes in the constructor
#         # print("nodear", node_adj)
#         # for xx in node_adj:
#         #     print("   ",xx)
#
#         for i, (ep_type, ep_node, ep_pos, ep_attr) in enumerate(node_adj):
#             k.nodes[node_name][i] = eval("kp." + ep_type)(ep_node, ep_pos, **ep_attr)
#
#     return k



if __name__ == "__main__":

    pass


    # k = PlanarDiagram()
    # k.add_vertices_from("ab")
    # k.add_crossings_from("cd")
    # k.set_arcs_from("a0b0,a1c0,a2d3,b1d2,b2c1,c2d1,c3d0")
    # k.name = "my diagram"
    # k.nodes["a"].attr = {"color": 3}
    # k.nodes["b"].attr = {"color": 7}
    # k.nodes["a"][0].attr = {"color": 8}
    # k.nodes["a"][1].attr = {"color": 9}
    # k.nodes["d"][3].attr = {"color": 10}
    # k.framing=3
    #
    # print(k)
    #
    # notation = to_knotpy_notation(k)
    # print(notation)
    #
    # k_parsed = from_knotpy_notation(notation)
    # print(k_parsed)
    #
    # print(k == k_parsed)

