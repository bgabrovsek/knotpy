from knotpy.classes.planardiagram import PlanarDiagram, Diagram, OrientedPlanarDiagram
from knotpy.reidemeister.reidemeister_4 import find_reidemeister_4_slide, reidemeister_4_slide
from knotpy.algorithms.topology import edges

def _fix_edge_colors(k:Diagram):
    for edge in edges(k):
        colors = {edge[-1].attr.get("color", None), edge[0].attr.get("color", None)}
        if len(colors) == 0:
            for ep in edge:
                if "color" in ep.attr:
                    del ep.attr["color"]
        elif len(colors) == 1:
            color = next(iter(colors))
            for ep in edge:
                if color is None:
                    if "color" in ep.attr:
                        del ep.attr["color"]
                else:
                    ep.attr["color"] = color
        else:
            raise ValueError("The diagram edge starts with more than one color")

def isolate_bonds(k:Diagram, bond_color, inplace=False):

    if not inplace:
        k = k.copy()

    isolated = False
    while not isolated:
        isolated = True
        for v, positions in find_reidemeister_4_slide(k):
            if any(k.endpoint_from_pair((v, p)).attr.get("color", None) == bond_color for p in positions):
                isolated = False
                reidemeister_4_slide(k, (v, positions), inplace=True)

                # fix coloring
                _fix_edge_colors(k)

                break

    return k

