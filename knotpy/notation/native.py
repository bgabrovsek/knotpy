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
# literal_eval = eval  # unsafe, kept for potential legacy reasons

from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram
from knotpy.classes.node import Vertex, Crossing, Node
from knotpy.classes.endpoint import OutgoingEndpoint, IngoingEndpoint, Endpoint


def _attr_to_str(attr: dict) -> str:
    """Convert a dictionary of attributes to a string representation."""
    return ",".join(f"{repr(key)}={repr(value)}" for key, value in attr.items())


def _node_to_str(node: Node) -> str:
    """Convert a node to a string representation."""
    ept = {Endpoint: "", OutgoingEndpoint: "o", IngoingEndpoint: "i"}
    return " ".join(f"{ep.node}{ep.position}{ept[type(ep)]}" for ep in node)


def to_knotpy_notation(k: PlanarDiagram) -> str:
    """Return KnotPy notation of planar diagram.

    Args:
        k: Planar diagram.

    Returns:
        KnotPy notation string.
    """
    ept = {Endpoint: "", OutgoingEndpoint: "o", IngoingEndpoint: "i"}
    _node_abbr = {Crossing: "X", Vertex: "V"}
    compact_notation = all(isinstance(node, str) and len(node) == 1 for node in k.nodes)

    if compact_notation:
        nodes_str = ""
        for node in sorted(k.nodes):
            nodes_str += (
                str(node)
                + "="
                + _node_abbr[type(k.nodes[node])]
                + "("
                + _node_to_str(k.nodes[node])
                + ") "
            )
        nodes_str = nodes_str[:-1]

        diagram_attr_str = _attr_to_str(k.attr)
        node_attr_str = " ".join(
            f"{node}:{{{_attr_to_str(k.nodes[node].attr)}}}"
            for node in sorted(k.nodes)
            if k.nodes[node].attr
        )
        endpoint_attr_str = " ".join(
            f"{ep.node}{ep.position}{ept[type(ep)]}:{{{_attr_to_str(ep.attr)}}}"
            for ep in sorted(k.endpoints)
            if ep.attr
        )

        parts = [diagram_attr_str, node_attr_str, endpoint_attr_str]
        while parts and not parts[-1]:
            parts = parts[:-1]

        return f"{nodes_str}" if not parts else f"{nodes_str} [{'; '.join(parts)}]"

    else:
        NotImplementedError(
            "Non-compact notation not implemented (vertex names must be single characters)."
        )
        return None


def _parse_attributes_dict(attr_string: str) -> dict:
    """Parse a string of key=value pairs into a dictionary using regex."""
    pattern = re.compile(r"'?(\w+)'?\s*=\s*('[^']*'|\d+|\[.*?\]|\{.*?\})")
    result = {}
    for key, value in pattern.findall(attr_string):
        result[key] = literal_eval(value)
    return result


def _parse_compact(notation: str) -> PlanarDiagram | OrientedPlanarDiagram:
    """Parse compact KnotPy notation into a PlanarDiagram."""
    if "→" in notation:
        notation = notation.replace(" → ", "=").replace("→", "=").replace("),", ")")

    _node_abbr = {"X": Crossing, "V": Vertex}
    definition_part, *attribute_parts = notation.split("[")
    attribute_string = "[".join(attribute_parts).rstrip("]") if attribute_parts else ""

    node_pattern = re.compile(r"(\w+)=([VX])\(([^)]+)\)")
    oriented = "i)" in notation or "o)" in notation
    k = OrientedPlanarDiagram() if oriented else PlanarDiagram()

    for match in node_pattern.finditer(definition_part):
        node, node_type, endpoints = match.groups()
        endpoints = endpoints.strip().split()
        k.add_node(node, create_using=_node_abbr[node_type], degree=len(endpoints))

        for pos, ep_str in enumerate(endpoints):
            if oriented:
                triple = tuple(
                    re.match(r"([a-zA-Z]+)(\d+)([io])", ep_str.strip()).groups()
                )
                k.set_endpoint(
                    (node, pos),
                    (triple[0], int(triple[1])),
                    create_using=OutgoingEndpoint if triple[2] == "o" else IngoingEndpoint,
                )
            else:
                pair = tuple(re.match(r"([a-zA-Z]+)(\d+)", ep_str.strip()).groups())
                k.set_endpoint((node, pos), (pair[0], int(pair[1])), create_using=Endpoint)

    attr_split = attribute_string.split(";")
    if len(attr_split) > 3:
        raise ValueError("Invalid attribute string format.")
    attr_split += [""] * (3 - len(attr_split))

    diagram_attr, node_attr, endpoint_attr = attr_split
    k.attr.update(_parse_attributes_dict(diagram_attr.strip()))

    node_attribute_pattern = re.compile(r"(\w+)\s*:\s*\{([^}]*)\}")
    for node, attr_str in node_attribute_pattern.findall(node_attr):
        k.nodes[node].attr.update(_parse_attributes_dict(attr_str.strip()))

    for ep, attr_str in node_attribute_pattern.findall(endpoint_attr):
        pair = tuple(re.match(r"([a-zA-Z]+)(\d+)", ep).groups())
        k.endpoint_from_pair((pair[0], int(pair[1]))).attr.update(
            _parse_attributes_dict(attr_str.strip())
        )

    return k


def from_knotpy_notation(notation: str) -> PlanarDiagram | OrientedPlanarDiagram:
    """Convert notation string into a PlanarDiagram."""
    compact_notation = True
    if compact_notation:
        return _parse_compact(notation)
    else:
        raise NotImplementedError()


if __name__ == "__main__":
    pass
