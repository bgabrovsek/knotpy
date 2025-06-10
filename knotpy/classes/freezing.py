from knotpy.classes.planardiagram import PlanarDiagram, OrientedPlanarDiagram

def frozen(*args, **kwargs):
    """Dummy method for raising errors when trying to modify frozen diagrams"""
    raise RuntimeError("Frozen diagrams cannot be modified")


def freeze(k: PlanarDiagram | OrientedPlanarDiagram):
    """Freeze the given planar diagram inplace so that it cannot be modified anymore."""
    k.frozen = True

    k.add_node = frozen
    k.add_nodes_from = frozen

    # if hasattr(k, "add_crossing"):
    #     k.add_crossing = frozen
    k.add_crossing = frozen
    k.add_crossings_from = frozen
    if hasattr(k, "add_virtual_crossing"):
        k.add_virtual_crossing = frozen
    if hasattr(k, "add_virtual_crossings_from"):
        k.add_virtual_crossings_from = frozen
    k.add_vertex = frozen
    k.add_vertices_from = frozen
    k.permute_node = frozen
    k.convert_node = frozen
    k.remove_node = frozen
    k.remove_nodes_from = frozen
    k.relabel_nodes = frozen
    k.set_endpoint = frozen
    k.remove_endpoint = frozen
    k.remove_endpoints_from = frozen
    k.set_arc = frozen
    k.set_arcs_from = frozen
    k.remove_arc = frozen
    k.remove_arcs_from = frozen

    #TODO: cannot override framing setter, raise error in setter
    #TODO freeze endpoint/attr, node/attr iteratively

    return k



def unfreeze(k: PlanarDiagram | OrientedPlanarDiagram):
    """Unfreeze the given planar diagram inplace so that it can again be modified. This is for example useful when
    we pop a diagram from a set and the set gets destroyed immediately (e.g. in a return call)."""
    k.frozen = False

    k.add_node = type(k).add_node.__get__(k)
    k.add_nodes_from = type(k).add_nodes_from.__get__(k)

    # if hasattr(k, "add_crossing"):
    #     k.add_crossing = frozen
    k.add_crossing = type(k).add_crossing.__get__(k)
    k.add_crossings_from = type(k).add_crossings_from.__get__(k)
    if hasattr(k, "add_virtual_crossing"):
        k.add_virtual_crossing = type(k).add_virtual_crossing.__get__(k)
    if hasattr(k, "add_virtual_crossings_from"):
        k.add_virtual_crossings_from = type(k).add_virtual_crossings_from.__get__(k)
    k.add_vertex = type(k).add_vertex.__get__(k)
    k.add_vertices_from = type(k).add_vertices_from.__get__(k)
    k.permute_node = type(k).permute_node.__get__(k)
    k.convert_node = type(k).convert_node.__get__(k)
    k.remove_node = type(k).remove_node.__get__(k)
    k.remove_nodes_from = type(k).remove_nodes_from.__get__(k)
    k.relabel_nodes = type(k).relabel_nodes.__get__(k)
    k.set_endpoint = type(k).set_endpoint.__get__(k)
    k.remove_endpoint = type(k).remove_endpoint.__get__(k)
    k.remove_endpoints_from = type(k).remove_endpoints_from.__get__(k)
    k.set_arc = type(k).set_arc.__get__(k)
    k.set_arcs_from = type(k).set_arcs_from.__get__(k)
    k.remove_arc = type(k).remove_arc.__get__(k)
    k.remove_arcs_from = type(k).remove_arcs_from.__get__(k)

    #TODO: cannot override framing setter, raise error in setter
    #TODO freeze endpoint/attr, node/attr iteratively

    return k