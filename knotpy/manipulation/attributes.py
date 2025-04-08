from knotpy import PlanarDiagram


def clear_node_attributes(k, attr=None):
    """Clear node attributes of the planar diagram k, or the list of planar diagrams k.

    This function operates in-place to remove specified attributes from nodes
    in a given object or collection of objects. If the collection is a list,
    set, or tuple, the function is applied recursively to each object within
    the collection. If the `attr` parameter is not specified, all attributes
    of the nodes are cleared.

    Args:
        k (Union[PlanarDiagram, List[PlanarDiagram], Set[PlanarDiagram]]):
            The object or a collection of objects whose node attributes
            are to be cleared.
        attr (Optional[Union[List, Set, Tuple, str]]): The attribute(s) to
            remove. Can be a single attribute (str), or a collection of
            attributes (list, set, or tuple). If None, all attributes
            will be cleared.
    """

    if isinstance(k, (list, set, tuple)):
        for sub_knot in k:
            clear_node_attributes(sub_knot, attr)
        return

    if isinstance(attr, (list, set, tuple)):
        for key in attr:
            clear_node_attributes(k, key)
        return

    if attr is None:
        for node in k.nodes:
            k.nodes[node].attr.clear()
    else:
        for node in k.nodes:
            if attr in k.nodes[node].attr:
                del k.nodes[node].attr[attr]


def clear_endpoint_attributes(k, attr=None):
    """Clear endpoint attributes of the planar diagram k, or the list of planar diagrams k.

    This function operates in-place to remove specified attributes from nodes
    in a given object or collection of objects. If the collection is a list,
    set, or tuple, the function is applied recursively to each object within
    the collection. If the `attr` parameter is not specified, all attributes
    of the nodes are cleared.

    Args:
        k (Union[PlanarDiagram, List[PlanarDiagram], Set[PlanarDiagram]]):
            The object or a collection of objects whose endpoint attributes
            are to be cleared.
        attr (Optional[Union[List, Set, Tuple, str]]): The attribute(s) to
            remove. Can be a single attribute (str), or a collection of
            attributes (list, set, or tuple). If None, all attributes
            will be cleared.
    """

    if isinstance(k, (list, set, tuple)):
        for sub_knot in k:
            clear_endpoint_attributes(sub_knot, attr)
        return

    if isinstance(attr, (list, set, tuple)):
        for key in attr:
            clear_endpoint_attributes(k, key)
        return

    if attr is None:
        for ep in k.endpoints:
            k.nodes[ep.node][ep.position].attr.clear()
    else:
        for ep in k.endpoints:
            if attr in k.nodes[ep.node][ep.position].attr:
                del k.nodes[ep.node][ep.position].attr[attr]


def clear_diagram_attributes(k, attr=None):
    """Clear main diagram-level attributes of the diagram k, or the list of planar diagrams k.

    Args:
        k (Union[PlanarDiagram, List[PlanarDiagram], Set[PlanarDiagram]]):
            The object or a collection of objects whose attributes  are to be cleared.
        attr (Optional[Union[List, Set, Tuple, str]]): The attribute(s) to
            remove. Can be a single attribute (str), or a collection of
            attributes (list, set, or tuple). If None, all attributes
            will be cleared.
    """

    if isinstance(k, (list, set, tuple)):
        for sub_knot in k:
            clear_diagram_attributes(sub_knot, attr)
        return

    if isinstance(attr, (list, set, tuple)):
        for key in attr:
            clear_diagram_attributes(k, key)
        return

    if attr is None:
        k.attr.clear()
    else:
        del k.attr[attr]


def clear_attributes(k: PlanarDiagram):
    """ Clear all attributes from a PlanarDiagram."""

    clear_node_attributes(k)
    clear_endpoint_attributes(k)
    clear_diagram_attributes(k)
