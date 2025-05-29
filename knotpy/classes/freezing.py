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
