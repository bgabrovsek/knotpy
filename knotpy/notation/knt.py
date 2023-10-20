"""
Default KnotPy notation with all diagram information stored. It is similar to EM notation.

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

__all__ = ["to_knot_notation", "from_knot_notation"]
__version__ = "0.1"
__author__ = "Boštjan Gabrovšek"

from knotpy.classes.planardiagram import PlanarDiagram


def _endpoint_knot_notation(ep, attributes) -> str:
    """Return string representing an endpoint. Example: "('a',3,{'color':'Orange'})"
    :param ep:
    :param attributes:
    :return: str
    """
    text = f"{repr(ep.node)},{ep.position}"
    if attributes:
        text += "," + repr(ep.attr).replace(' ', '')
    return "(" + text + ")"


def _node_knot_notation(k: PlanarDiagram, node, attributes: bool) -> str:
    """Return string representing a node. Example: "Vertex [('a',3,{'color':'Orange'})] {}".
    If data is False, the return string is "Vertex [('a',3)]"
    :param k: knot diagram
    :param node: which node to convert
    :param attributes: add additional data (attributes)
    :return: str
    """
    text = f"{type(k.nodes[node]).__name__} {node} "
    text += "[" + ",".join(_endpoint_knot_notation(ep, attributes) for ep in k.nodes[node]) + "]"
    if attributes:
        text += " " + repr(k.nodes[node].attr).replace(' ', '')
    return text


def to_knot_notation(k, attributes=True, separator=";") -> str:
    """Returns KnotPy notation of planar diagram.
    Example:
        "SpatialGraph {'name':'x1','color':'red'}
        Vertex a [('b',0,{'color':'Orange'})] {}
        Vertex b [('a',0,{'color':'Orange'})] {}"
    """
    if attributes:
        texts = [type(k).__name__ + " " + str(k.attr).replace(" ", "")]  # knot info
    else:
        texts = [type(k).__name__]

    texts += [_node_knot_notation(k, node, attributes) for node in k.nodes]

    if separator == ",":
        texts = [t.replace(",", ";") for t in texts]

    return separator.join(texts)


def from_knot_notation(text, separator=";") -> str:
    """

    :param text:
    :param separator:
    :return:
    """
    raise NotImplementedError()
    return ""

def _test_knot_notation():
    from knotpy.generate.example import example_spatial_graph
    k = example_spatial_graph()
    notation = to_knot_notation(k, attributes=True, separator="\n")
    print(notation)


if __name__ == "__main__":
    _test_knot_notation()