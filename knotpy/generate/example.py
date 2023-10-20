__all__ = ['example_spatial_graph']
__version__ = '0.1'
__author__ = 'Boštjan Gabrovšek'

def example_spatial_graph():
    from knotpy.classes.spatialgraph import SpatialGraph
    k = SpatialGraph(name="x1", color="red")
    k.add_crossings_from("ab", color="blue")
    k.add_vertices_from("uv")
    k.set_arc([("a", 0), ("b", 0)], color="Orange")
    k.set_arc([("a", 1), ("b", 2)], color="Orange")
    k.set_arc([("a", 2), ("b", 1)], color="Orange")
    k.set_arc([("a", 3), ("v", 0)], color="Orange")
    k.set_arc([("b", 3), ("u", 0)], color="Orange")
    return k


def trefoil_knot():
    from knotpy.classes.knot import Knot
    k = Knot(name="Trefoil")
    k.add_crossings_from("abc")
    k.set_arc([("a", 0), ("c", 3)])
    k.set_arc([("a", 1), ("c", 2)])
    k.set_arc([("a", 2), ("b", 1)])
    k.set_arc([("a", 3), ("b", 0)])
    k.set_arc([("b", 2), ("c", 1)])
    k.set_arc([("b", 3), ("c", 0)])
    return k


def trefoil_theta():
    from knotpy.classes.spatialgraph import SpatialGraph
    k = SpatialGraph(name="Theta trefoil")
    k.add_crossings_from("abc")
    k.add_vertices_from("de")
    k.set_arc([("a", 0), ("c", 3)])
    k.set_arc([("a", 1), ("c", 2)])
    k.set_arc([("a", 2), ("e", 0)])
    k.set_arc([("a", 3), ("d", 0)])
    k.set_arc([("b", 0), ("d", 2)])
    k.set_arc([("b", 1), ("e", 1)])
    k.set_arc([("b", 2), ("c", 1)])
    k.set_arc([("b", 3), ("c", 0)])
    k.set_arc([("d", 1), ("e", 2)])
    return k


def handcuff_theta():
    from knotpy.classes.spatialgraph import SpatialGraph
    k = SpatialGraph(name="Theta trefoil")
    k.add_crossings_from("abc")
    k.add_vertices_from("de")
    k.set_arc([("a", 0), ("b", 3)])
    k.set_arc([("a", 1), ("b", 2)])
    k.set_arc([("a", 2), ("c", 0)])
    k.set_arc([("a", 3), ("d", 0)])
    k.set_arc([("b", 0), ("d", 2)])
    k.set_arc([("b", 1), ("c", 1)])
    k.set_arc([("c", 2), ("d", 1)])
    return k


def oriented_trefoil():
    k = trefoil_knot()
    return k

# print(trefoil_knot())
# print(trefoil_theta())
# print(handcuff_theta())
# print(oriented_trefoil())
